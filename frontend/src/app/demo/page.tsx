'use client';

import { CardFan3D } from '@/components/animations';

/**
 * Demo page showcasing the 3D Card Fan animation
 * Visit /demo to see the animation in action
 */
export default function DemoPage() {
  return (
    <main>
      {/* Default: Fan out on page load */}
      <CardFan3D 
        config={{
          dealDuration: 0.8,
          dealDelay: 0.12,
          holdDuration: 1800,
          arcHeight: 170,
        }}
      />
    </main>
  );
}
