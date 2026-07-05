package com.finbuddy.connector.sms

import com.finbuddy.connector.data.model.ParsedTransaction
import com.finbuddy.connector.data.model.SmsMessage
import com.finbuddy.connector.data.model.TransactionCategory
import com.finbuddy.connector.data.model.TransactionType
import java.util.regex.Pattern

/**
 * SMS Parser for extracting financial transaction data from bank SMS messages.
 * Matches the backend Transaction model structure for seamless database integration.
 */
class SmsParser {

    // ==================== BANK SENDER PATTERNS ====================
    
    // Common bank sender IDs (Indian banks + payment services)
    private val bankSenderPatterns = listOf(
        // Indian Banks
        ".*HDFC.*", ".*ICICI.*", ".*SBI.*", ".*AXIS.*", ".*KOTAK.*",
        ".*IDFC.*", ".*YES.*BANK.*", ".*PNB.*", ".*BOB.*", ".*CITI.*",
        ".*INDUS.*", ".*RBL.*", ".*FEDERAL.*", ".*CANARA.*", ".*UNION.*",
        ".*IDBI.*", ".*IOB.*", ".*INDIAN.*", ".*UCO.*", ".*SYNDICATE.*",
        ".*ALLAHABAD.*", ".*ANDHRA.*", ".*ORIENTAL.*", ".*VIJAYA.*",
        ".*BARODA.*", ".*DENA.*", ".*CENTRAL.*", ".*CORPORATION.*",
        // Payment Services
        ".*PAYTM.*", ".*GPAY.*", ".*PHONEPE.*", ".*AMAZONPAY.*", ".*MOBIKWIK.*",
        ".*FREECHARGE.*", ".*UPI.*", ".*BHIM.*", ".*CRED.*", ".*SLICE.*",
        ".*SIMPL.*", ".*LAZYPAY.*", ".*POSTPE.*", ".*JUPITER.*", ".*FI.*",
        // Credit Cards
        ".*AMEX.*", ".*VISA.*", ".*MASTERCARD.*", ".*RUPAY.*", ".*DINERS.*",
        // Generic patterns
        ".*BANK.*", ".*CREDIT.*", ".*DEBIT.*", ".*WALLET.*", ".*CARD.*"
    ).map { Pattern.compile(it, Pattern.CASE_INSENSITIVE) }

    // ==================== AMOUNT PATTERNS ====================
    
    private val amountPatterns = listOf(
        // Rs. or INR or ₹ followed by amount
        Pattern.compile("(?:RS\\.?|INR|₹)\\s*([\\d,]+\\.?\\d*)", Pattern.CASE_INSENSITIVE),
        // Amount with keywords
        Pattern.compile("(?:amount|amt|rs|inr)[:\\s]*(?:RS\\.?|INR|₹)?\\s*([\\d,]+\\.?\\d*)", Pattern.CASE_INSENSITIVE),
        // Amount before "has been" or "is"
        Pattern.compile("([\\d,]+\\.?\\d*)\\s*(?:has been|is|was|debited|credited)", Pattern.CASE_INSENSITIVE),
        // For patterns like "debited for 500"
        Pattern.compile("(?:debited|credited|paid|received)\\s*(?:for|of|with)?\\s*(?:RS\\.?|INR|₹)?\\s*([\\d,]+\\.?\\d*)", Pattern.CASE_INSENSITIVE)
    )

    // ==================== TRANSACTION TYPE KEYWORDS ====================
    
    private val debitKeywords = listOf(
        "debited", "debit", "withdrawn", "paid", "spent", "purchase",
        "payment", "transfer to", "sent", "deducted", "charged", "used",
        "txn", "transaction at", "pos", "atm withdrawal", "bill payment",
        "emi", "auto-debit", "mandate", "subscription"
    )

    private val creditKeywords = listOf(
        "credited", "credit", "received", "deposited", "refund",
        "cashback", "transfer from", "added", "reversed", "salary",
        "bonus", "interest", "dividend", "reward", "money received"
    )

    // ==================== ACCOUNT NUMBER PATTERNS ====================
    
    private val accountPatterns = listOf(
        Pattern.compile("(?:a/c|ac|account|acct)[:\\s]*(?:no\\.?)?[:\\s]*[xX*]+([\\d]{4,})", Pattern.CASE_INSENSITIVE),
        Pattern.compile("[xX*]+([\\d]{4})", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(?:card|ending|linked)[:\\s]*(?:with|in)?[:\\s]*([\\d]{4})", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(?:from|to)\\s+(?:a/c|ac)?\\s*[xX*]*([\\d]{4,})", Pattern.CASE_INSENSITIVE)
    )

    // ==================== BALANCE PATTERNS ====================
    
    private val balancePatterns = listOf(
        Pattern.compile("(?:bal|balance|avl\\.?\\s*bal|available)[:\\s]*(?:RS\\.?|INR|₹)?\\s*([\\d,]+\\.?\\d*)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(?:available|avbl)[:\\s]*(?:RS\\.?|INR|₹)?\\s*([\\d,]+\\.?\\d*)", Pattern.CASE_INSENSITIVE)
    )

    // ==================== REFERENCE NUMBER PATTERNS ====================
    
    private val refPatterns = listOf(
        Pattern.compile("(?:ref|reference|txn|transaction)[:\\s#]*([A-Za-z0-9]+)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(?:utr|imps|neft|rtgs|upi)[:\\s]*([A-Za-z0-9]+)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(?:order|id)[:\\s#]*([A-Za-z0-9]+)", Pattern.CASE_INSENSITIVE)
    )

    // ==================== MERCHANT PATTERNS ====================
    
    private val merchantPatterns = listOf(
        Pattern.compile("(?:at|to|from|@|paid to|sent to|received from)[:\\s]*([A-Za-z0-9\\s&'\\-\\.]+?)(?:\\s+on|\\s+ref|\\s+txn|\\s+upi|\\.|,|$)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(?:vpa|upi)[:\\s]*([a-z0-9@\\-\\.]+)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(?:pos|ecom|online)[:\\s]*([A-Za-z0-9\\s&'\\-]+?)(?:\\s+on|\\.|,|$)", Pattern.CASE_INSENSITIVE)
    )

    // ==================== CATEGORY KEYWORDS (Matching Backend) ====================
    
    private val categoryKeywords = mapOf(
        TransactionCategory.BILLS to listOf(
            "electricity", "electric", "water", "gas", "broadband", "internet",
            "mobile", "phone", "recharge", "dth", "dish", "cable", "wifi",
            "postpaid", "prepaid", "utility", "municipal", "tax", "emi", "loan"
        ),
        TransactionCategory.ESSENTIALS to listOf(
            "grocery", "groceries", "supermarket", "vegetables", "milk",
            "provisions", "kirana", "bigbasket", "grofers", "blinkit",
            "zepto", "instamart", "dmart", "reliance fresh", "more",
            "medicine", "pharmacy", "medical", "hospital", "clinic", "doctor"
        ),
        TransactionCategory.SPENDS to listOf(
            "restaurant", "cafe", "coffee", "zomato", "swiggy", "food",
            "dining", "hotel", "movie", "entertainment", "shopping", "mall",
            "amazon", "flipkart", "myntra", "ajio", "fashion", "clothes",
            "electronics", "appliance", "furniture", "decor"
        ),
        TransactionCategory.INVESTMENTS to listOf(
            "mutual", "fund", "stock", "share", "sip", "investment", "trading",
            "zerodha", "groww", "upstox", "kite", "demat", "equity", "mf",
            "nps", "ppf", "elss", "bonds", "gold", "etf"
        ),
        TransactionCategory.INCOME to listOf(
            "salary", "credit", "refund", "cashback", "reward", "bonus",
            "interest", "dividend", "rent received", "payment received"
        ),
        TransactionCategory.TRANSFER to listOf(
            "transfer", "neft", "imps", "rtgs", "upi", "self transfer",
            "own account", "fund transfer"
        ),
        TransactionCategory.SAVINGS to listOf(
            "fd", "fixed deposit", "rd", "recurring", "savings", "deposit"
        ),
        TransactionCategory.NEEDS to listOf(
            "rent", "housing", "maintenance", "society", "insurance",
            "premium", "education", "school", "college", "tuition"
        )
    )

    // ==================== PUBLIC METHODS ====================

    /**
     * Check if sender is a financial institution
     */
    fun isFinancialSender(sender: String): Boolean {
        return bankSenderPatterns.any { pattern ->
            pattern.matcher(sender).matches() || pattern.matcher(sender).find()
        }
    }

    /**
     * Parse SMS message and extract transaction details
     */
    fun parseSms(sms: SmsMessage): ParsedTransaction {
        val body = sms.body
        val sender = sms.sender

        // Check if it's a financial SMS
        val isFinancial = isFinancialMessage(body)

        if (!isFinancial) {
            return ParsedTransaction(
                originalSms = sms,
                amount = null,
                transactionType = null,
                merchant = null,
                accountNumber = null,
                bankName = extractBankName(sender),
                balance = null,
                referenceNumber = null,
                category = TransactionCategory.OTHER,
                isFinancialSms = false
            )
        }

        val transactionType = extractTransactionType(body)
        val merchant = extractMerchant(body)
        val category = categorizeTransaction(body, merchant, transactionType)

        return ParsedTransaction(
            originalSms = sms,
            amount = extractAmount(body),
            transactionType = transactionType,
            merchant = merchant,
            accountNumber = extractAccountNumber(body),
            bankName = extractBankName(sender),
            balance = extractBalance(body),
            referenceNumber = extractReferenceNumber(body),
            category = category,
            isFinancialSms = true
        )
    }

    // ==================== PRIVATE METHODS ====================

    private fun isFinancialMessage(body: String): Boolean {
        val lowerBody = body.lowercase()
        
        // Must have transaction keyword
        val hasTransactionKeyword = debitKeywords.any { lowerBody.contains(it) } ||
                creditKeywords.any { lowerBody.contains(it) }

        // Must have amount pattern
        val hasAmount = amountPatterns.any { it.matcher(body).find() }

        // Exclude OTP/verification messages
        val isOtp = lowerBody.contains("otp") || 
                    lowerBody.contains("verification") ||
                    lowerBody.contains("one time password") ||
                    lowerBody.contains("code is")

        return hasTransactionKeyword && hasAmount && !isOtp
    }

    private fun extractAmount(body: String): Double? {
        for (pattern in amountPatterns) {
            val matcher = pattern.matcher(body)
            if (matcher.find()) {
                val amountStr = matcher.group(1)
                    ?.replace(",", "")
                    ?.trim()
                val amount = amountStr?.toDoubleOrNull()
                // Validate reasonable amount (not OTP or random numbers)
                if (amount != null && amount > 0 && amount < 100000000) {
                    return amount
                }
            }
        }
        return null
    }

    private fun extractTransactionType(body: String): TransactionType {
        val lowerBody = body.lowercase()
        
        // Check debit keywords first (more common)
        if (debitKeywords.any { lowerBody.contains(it) }) {
            return TransactionType.DEBIT
        }
        
        // Check credit keywords
        if (creditKeywords.any { lowerBody.contains(it) }) {
            return TransactionType.CREDIT
        }
        
        return TransactionType.DEBIT // Default to debit
    }

    private fun extractAccountNumber(body: String): String? {
        for (pattern in accountPatterns) {
            val matcher = pattern.matcher(body)
            if (matcher.find()) {
                return matcher.group(1)?.trim()
            }
        }
        return null
    }

    private fun extractBankName(sender: String): String? {
        val upperSender = sender.uppercase()
        
        return when {
            upperSender.contains("HDFC") -> "HDFC Bank"
            upperSender.contains("ICICI") -> "ICICI Bank"
            upperSender.contains("SBI") || upperSender.contains("STATE BANK") -> "State Bank of India"
            upperSender.contains("AXIS") -> "Axis Bank"
            upperSender.contains("KOTAK") -> "Kotak Mahindra Bank"
            upperSender.contains("IDFC") -> "IDFC First Bank"
            upperSender.contains("YES") -> "Yes Bank"
            upperSender.contains("PNB") -> "Punjab National Bank"
            upperSender.contains("BOB") || upperSender.contains("BARODA") -> "Bank of Baroda"
            upperSender.contains("CITI") -> "Citibank"
            upperSender.contains("INDUS") -> "IndusInd Bank"
            upperSender.contains("RBL") -> "RBL Bank"
            upperSender.contains("FEDERAL") -> "Federal Bank"
            upperSender.contains("CANARA") -> "Canara Bank"
            upperSender.contains("UNION") -> "Union Bank"
            upperSender.contains("IDBI") -> "IDBI Bank"
            upperSender.contains("PAYTM") -> "Paytm Payments Bank"
            upperSender.contains("GPAY") || upperSender.contains("GOOGLEPAY") -> "Google Pay"
            upperSender.contains("PHONEPE") -> "PhonePe"
            upperSender.contains("AMAZON") -> "Amazon Pay"
            upperSender.contains("CRED") -> "CRED"
            upperSender.contains("SLICE") -> "Slice"
            upperSender.contains("JUPITER") -> "Jupiter"
            upperSender.contains("FI") -> "Fi Money"
            else -> null
        }
    }

    private fun extractBalance(body: String): Double? {
        for (pattern in balancePatterns) {
            val matcher = pattern.matcher(body)
            if (matcher.find()) {
                val balanceStr = matcher.group(1)
                    ?.replace(",", "")
                    ?.trim()
                return balanceStr?.toDoubleOrNull()
            }
        }
        return null
    }

    private fun extractReferenceNumber(body: String): String? {
        for (pattern in refPatterns) {
            val matcher = pattern.matcher(body)
            if (matcher.find()) {
                val ref = matcher.group(1)?.trim()
                // Validate it looks like a reference (not just a word)
                if (ref != null && ref.length >= 6) {
                    return ref
                }
            }
        }
        return null
    }

    private fun extractMerchant(body: String): String? {
        for (pattern in merchantPatterns) {
            val matcher = pattern.matcher(body)
            if (matcher.find()) {
                val merchant = matcher.group(1)?.trim()
                // Clean up merchant name
                return merchant
                    ?.replace(Regex("\\s+"), " ")
                    ?.take(100)
                    ?.trim()
            }
        }
        return null
    }

    /**
     * Categorize transaction based on SMS content, merchant, and type
     * Matches backend TransactionCategory enum
     */
    private fun categorizeTransaction(
        body: String, 
        merchant: String?, 
        transactionType: TransactionType
    ): TransactionCategory {
        val lowerBody = body.lowercase()
        val merchantLower = merchant?.lowercase() ?: ""
        
        // Check each category's keywords
        for ((category, keywords) in categoryKeywords) {
            if (keywords.any { keyword -> 
                lowerBody.contains(keyword) || merchantLower.contains(keyword) 
            }) {
                return category
            }
        }
        
        // Default based on transaction type
        return when (transactionType) {
            TransactionType.CREDIT -> TransactionCategory.INCOME
            TransactionType.DEBIT -> TransactionCategory.SPENDS
        }
    }
}
