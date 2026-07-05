"""
OCR Service for extracting transaction data from images and documents
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64
import io

from app.core.logging import get_logger
from app.config import settings


logger = get_logger(__name__)


class OCRService:
    """
    Service for OCR-based transaction extraction.
    
    Supports:
    - Bank SMS messages
    - Receipt images
    - Bank statement PDFs
    """
    
    # Common transaction patterns for Indian banks
    SMS_PATTERNS = {
        "debit": [
            r"(?:debited|withdrawn|spent|paid).*?(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            r"(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:debited|withdrawn)",
        ],
        "credit": [
            r"(?:credited|received|deposited).*?(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            r"(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:credited|received)",
        ],
        "upi": [
            r"upi.*?(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            r"(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?).*?upi",
        ],
        "reference": [
            r"(?:ref|txn|transaction)\s*(?:no\.?|id|#)?\s*[:.]?\s*(\w+)",
        ],
        "balance": [
            r"(?:bal|balance|avl\.? bal).*?(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        ],
        "account": [
            r"(?:a/c|ac|account).*?(\d{4})",
            r"xx+(\d{4})",
        ],
        "merchant": [
            r"(?:to|at|from)\s+([A-Za-z\s]+?)(?:\s+on|\s+ref|\s+upi|$)",
        ]
    }
    
    def __init__(self):
        self.use_vision = bool(settings.OPENAI_API_KEY)
    
    async def extract_from_sms(self, sms_text: str) -> Dict[str, Any]:
        """
        Extract transaction details from SMS text.
        
        Args:
            sms_text: Raw SMS message text
            
        Returns:
            Extracted transaction details
        """
        sms_text = sms_text.lower()
        result = {
            "type": None,
            "amount": None,
            "reference": None,
            "balance": None,
            "account_last4": None,
            "merchant": None,
            "raw_text": sms_text,
            "confidence": 0.0
        }
        
        # Detect transaction type
        if any(keyword in sms_text for keyword in ["debit", "withdrawn", "spent", "paid"]):
            result["type"] = "debit"
        elif any(keyword in sms_text for keyword in ["credit", "received", "deposited"]):
            result["type"] = "credit"
        
        # Extract amount
        for pattern_type in ["debit", "credit", "upi"]:
            for pattern in self.SMS_PATTERNS[pattern_type]:
                match = re.search(pattern, sms_text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(",", "")
                    try:
                        result["amount"] = float(amount_str)
                        if not result["type"]:
                            result["type"] = pattern_type if pattern_type != "upi" else "debit"
                        break
                    except ValueError:
                        continue
            if result["amount"]:
                break
        
        # Extract reference number
        for pattern in self.SMS_PATTERNS["reference"]:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                result["reference"] = match.group(1)
                break
        
        # Extract balance
        for pattern in self.SMS_PATTERNS["balance"]:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                balance_str = match.group(1).replace(",", "")
                try:
                    result["balance"] = float(balance_str)
                except ValueError:
                    pass
                break
        
        # Extract account
        for pattern in self.SMS_PATTERNS["account"]:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                result["account_last4"] = match.group(1)
                break
        
        # Calculate confidence
        fields_found = sum([
            result["type"] is not None,
            result["amount"] is not None,
            result["reference"] is not None,
            result["balance"] is not None,
            result["account_last4"] is not None
        ])
        result["confidence"] = fields_found / 5.0
        
        logger.info(
            "SMS extraction complete",
            fields_found=fields_found,
            confidence=result["confidence"]
        )
        
        return result
    
    async def extract_from_image(
        self,
        image_data: bytes,
        image_type: str = "receipt"
    ) -> Dict[str, Any]:
        """
        Extract transaction data from image using vision model.
        
        Args:
            image_data: Image bytes
            image_type: Type of image (receipt, statement)
            
        Returns:
            Extracted data
        """
        if not self.use_vision:
            return {
                "error": "Vision API not configured",
                "suggestion": "Set OPENAI_API_KEY for image processing"
            }
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Encode image
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Use vision model
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Extract transaction details from this {image_type}.
                                Return a JSON with:
                                - amount: transaction amount
                                - date: transaction date
                                - merchant: merchant/store name
                                - items: list of items if receipt
                                - total: total amount
                                - payment_method: cash/card/upi
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )
            
            return {
                "extracted": response.choices[0].message.content,
                "image_type": image_type
            }
            
        except Exception as e:
            logger.error("Image extraction failed", error=str(e))
            return {"error": str(e)}
    
    async def extract_from_pdf(
        self,
        pdf_bytes: bytes
    ) -> List[Dict[str, Any]]:
        """
        Extract transactions from bank statement PDF.
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            List of extracted transactions
        """
        try:
            import fitz  # PyMuPDF
            
            transactions = []
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page in doc:
                text = page.get_text()
                # Parse statement format
                lines = text.split('\n')
                
                for line in lines:
                    # Look for transaction patterns
                    date_pattern = r'(\d{2}[/-]\d{2}[/-]\d{2,4})'
                    amount_pattern = r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:Dr|Cr)?'
                    
                    date_match = re.search(date_pattern, line)
                    amount_match = re.search(amount_pattern, line)
                    
                    if date_match and amount_match:
                        transactions.append({
                            "date": date_match.group(1),
                            "amount": float(amount_match.group(1).replace(",", "")),
                            "description": line.strip(),
                            "type": "debit" if "Dr" in line else "credit" if "Cr" in line else None
                        })
            
            doc.close()
            
            return transactions
            
        except ImportError:
            logger.warning("PyMuPDF not installed for PDF processing")
            return [{"error": "PDF processing requires PyMuPDF"}]
        except Exception as e:
            logger.error("PDF extraction failed", error=str(e))
            return [{"error": str(e)}]
    
    async def batch_process_sms(
        self,
        sms_list: List[str]
    ) -> List[Dict[str, Any]]:
        """Process multiple SMS messages."""
        results = []
        for sms in sms_list:
            result = await self.extract_from_sms(sms)
            if result.get("amount"):
                results.append(result)
        return results


# Singleton instance
ocr_service = OCRService()
