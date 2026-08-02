import type { PropsWithChildren } from 'react'
import { motion, useReducedMotion } from 'framer-motion'

/** Shared, restrained motion primitives that respect a user's reduced-motion setting. */
export function Reveal({ children, delay = 0, className }: PropsWithChildren<{ delay?: number; className?: string }>) {
  const reduced = useReducedMotion()
  return <motion.div className={className} initial={reduced ? false : { opacity: 0, y: 18 }} whileInView={reduced ? {} : { opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.2 }} transition={{ duration: .5, delay, ease: [0.22, 1, 0.36, 1] }}>{children}</motion.div>
}

export function HoverCard({ children, className }: PropsWithChildren<{ className?: string }>) {
  const reduced = useReducedMotion()
  return <motion.div className={className} whileHover={reduced ? {} : { y: -5, scale: 1.01 }} transition={{ type: 'spring', stiffness: 360, damping: 24 }}>{children}</motion.div>
}
