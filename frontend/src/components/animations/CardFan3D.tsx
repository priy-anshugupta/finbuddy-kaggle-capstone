'use client';

import React, { useEffect, useRef } from 'react';
import { motion, useAnimation } from 'framer-motion';
import styles from './CardFan3D.module.css';

// =============================================================================
// CONFIGURATION - Credit Card Shuffle/Deal Animation
// =============================================================================
interface CardFanConfig {
  /** Duration of dealing a single card */
  dealDuration: number;
  /** How long to pause before dealing next card */
  dealDelay: number;
  /** How long cards stay stacked before reshuffling */
  holdDuration: number;
  /** Arc height of the deal curve */
  arcHeight: number;
}

interface CreditCardProps {
  id: number;
  cardNumber: string;
  cardHolder: string;
  expiry: string;
  type: 'visa' | 'mastercard' | 'amex';
  gradient: string;
}

interface CardFan3DProps {
  cards?: CreditCardProps[];
  config?: Partial<CardFanConfig>;
}

// Default configuration
const defaultConfig: CardFanConfig = {
  dealDuration: 0.6,
  dealDelay: 0.15,
  holdDuration: 1500,
  arcHeight: 150,
};

// Default credit cards
const defaultCards: CreditCardProps[] = [
  { 
    id: 1, 
    cardNumber: '•••• •••• •••• 4532', 
    cardHolder: 'JOHN DOE', 
    expiry: '12/28',
    type: 'visa',
    gradient: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
  },
  { 
    id: 2, 
    cardNumber: '•••• •••• •••• 8741', 
    cardHolder: 'JOHN DOE', 
    expiry: '03/27',
    type: 'mastercard',
    gradient: 'linear-gradient(135deg, #2d3436 0%, #636e72 100%)'
  },
  { 
    id: 3, 
    cardNumber: '•••• •••• •••• 2156', 
    cardHolder: 'JOHN DOE', 
    expiry: '09/26',
    type: 'visa',
    gradient: 'linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #2d2d2d 100%)'
  },
  { 
    id: 4, 
    cardNumber: '•••• •••• •••• 9923', 
    cardHolder: 'JOHN DOE', 
    expiry: '06/29',
    type: 'amex',
    gradient: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)'
  },
  { 
    id: 5, 
    cardNumber: '•••• •••• •••• 3347', 
    cardHolder: 'JOHN DOE', 
    expiry: '11/27',
    type: 'mastercard',
    gradient: 'linear-gradient(135deg, #4a1942 0%, #1a1a2e 100%)'
  },
];

// =============================================================================
// 3D MATH EXPLANATION - Card Dealing Animation
// =============================================================================
/**
 * Card dealing animation simulates shuffling from right to left:
 * 
 * 1. Cards start stacked on the RIGHT side of the screen
 * 2. Each card "deals" in an arc curve to the LEFT side
 * 3. Cards stack up on the left with slight rotation offset
 * 4. After all cards are dealt, they slide back and repeat
 * 
 * The arc trajectory uses a combination of:
 * - translateX: Moves card from right to left
 * - translateY: Creates the arc (peaks in middle via keyframes)
 * - rotateZ: Adds spin during the deal
 * - rotateY: 3D tilt effect
 */

export default function CardFan3D({ 
  cards = defaultCards, 
  config: userConfig = {},
}: CardFan3DProps) {
  const config = { ...defaultConfig, ...userConfig };
  const controls = useAnimation();
  const isAnimating = useRef(false);
  const [isMounted, setIsMounted] = React.useState(false);

  const numCards = cards.length;

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Animation loop: deal from right to left, then reset
  useEffect(() => {
    if (!isMounted) return;
    
    let isCancelled = false;
    
    const animationLoop = async () => {
      if (isAnimating.current) return;
      isAnimating.current = true;

      // Small delay to ensure controls are ready
      await new Promise(r => setTimeout(r, 100));

      while (!isCancelled) {
        try {
          // Reset all cards to right stack
          await controls.start('rightStack');
          
          // Wait before dealing
          await new Promise(r => setTimeout(r, 600));
          
          if (isCancelled) break;
          
          // Deal cards one by one to left
          await controls.start('dealToLeft');
          
          // Hold the left stack
          await new Promise(r => setTimeout(r, config.holdDuration));
          
          if (isCancelled) break;
          
          // Deal back to right
          await controls.start('dealToRight');
          
          // Hold the right stack
          await new Promise(r => setTimeout(r, config.holdDuration));
        } catch (e) {
          // Animation was interrupted, exit loop
          break;
        }
      }
    };

    animationLoop();
    
    return () => {
      isCancelled = true;
      isAnimating.current = false;
    };
  }, [controls, config.holdDuration, isMounted]);

  // Card type logos
  const getCardLogo = (type: CreditCardProps['type']) => {
    switch (type) {
      case 'visa':
        return <span className={styles.cardLogo}>VISA</span>;
      case 'mastercard':
        return (
          <div className={styles.mastercardLogo}>
            <div className={styles.mcCircle1} />
            <div className={styles.mcCircle2} />
          </div>
        );
      case 'amex':
        return <span className={styles.cardLogo}>AMEX</span>;
    }
  };

  if (!isMounted) {
    return (
      <div className={styles.container}>
        <div className={styles.dealArea} />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Deal area spanning the screen */}
      <div className={styles.dealArea}>
        {cards.map((card, index) => {
          // Stack offsets for left and right positions
          const stackOffset = index * 3;
          const rotationOffset = (index - numCards / 2) * 2;
          
          const cardVariants = {
            // Cards stacked on the right (far edge)
            rightStack: {
              x: '45vw',
              y: stackOffset,
              rotateZ: rotationOffset,
              rotateY: -15,
              rotateX: 5,
              scale: 1,
              transition: {
                duration: config.dealDuration,
                delay: (numCards - 1 - index) * config.dealDelay,
                ease: [0.25, 0.46, 0.45, 0.94],
              }
            },
            // Deal to left stack with arc (far edge)
            dealToLeft: {
              x: '-45vw',
              y: [stackOffset, -config.arcHeight, stackOffset],
              rotateZ: [rotationOffset, rotationOffset + 180, -rotationOffset],
              rotateY: [-15, 0, 15],
              rotateX: [5, -10, 5],
              scale: [1, 1.1, 1],
              transition: {
                duration: config.dealDuration * 1.5,
                delay: index * config.dealDelay,
                ease: [0.25, 0.46, 0.45, 0.94],
                times: [0, 0.5, 1],
              }
            },
            // Deal back to right with arc (far edge)
            dealToRight: {
              x: '45vw',
              y: [stackOffset, -config.arcHeight, stackOffset],
              rotateZ: [-rotationOffset, -rotationOffset - 180, rotationOffset],
              rotateY: [15, 0, -15],
              rotateX: [5, -10, 5],
              scale: [1, 1.1, 1],
              transition: {
                duration: config.dealDuration * 1.5,
                delay: (numCards - 1 - index) * config.dealDelay,
                ease: [0.25, 0.46, 0.45, 0.94],
                times: [0, 0.5, 1],
              }
            },
          };

          return (
            <motion.div
              key={card.id}
              className={styles.cardWrapper}
              initial="rightStack"
              animate={controls}
              variants={cardVariants}
              style={{
                zIndex: numCards - index,
                transformStyle: 'preserve-3d',
              }}
            >
              {/* Credit Card */}
              <div 
                className={styles.creditCard}
                style={{ background: card.gradient }}
              >
                {/* Glass overlay */}
                <div className={styles.glassOverlay} />
                
                {/* Chip */}
                <div className={styles.chip}>
                  <div className={styles.chipLines}>
                    <div /><div /><div /><div />
                  </div>
                </div>
                
                {/* Contactless icon */}
                <div className={styles.contactless}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z" opacity="0.3"/>
                    <path d="M7.5 12c0-2.5 2-4.5 4.5-4.5" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                    <path d="M5.5 12c0-3.6 2.9-6.5 6.5-6.5" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                    <path d="M3.5 12c0-4.7 3.8-8.5 8.5-8.5" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                  </svg>
                </div>
                
                {/* Card number */}
                <div className={styles.cardNumber}>
                  {card.cardNumber}
                </div>
                
                {/* Card details row */}
                <div className={styles.cardDetails}>
                  <div className={styles.cardHolder}>
                    <span className={styles.label}>CARD HOLDER</span>
                    <span className={styles.value}>{card.cardHolder}</span>
                  </div>
                  <div className={styles.cardExpiry}>
                    <span className={styles.label}>EXPIRES</span>
                    <span className={styles.value}>{card.expiry}</span>
                  </div>
                </div>
                
                {/* Card logo */}
                <div className={styles.cardBrand}>
                  {getCardLogo(card.type)}
                </div>
                
                {/* Shine effect */}
                <div className={styles.shine} />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Curved path indicator (visual guide) */}
      <div className={styles.arcPath} />
    </div>
  );
}
