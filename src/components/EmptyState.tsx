'use client'

import { motion } from 'framer-motion'
import { FileVideo, Sparkles } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

export default function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-16 px-6 text-center">
          <motion.div
            animate={{
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatDelay: 3,
            }}
            className="mb-6"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full" />
              <div className="relative w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                <FileVideo className="h-10 w-10 text-primary" />
              </div>
            </div>
          </motion.div>
          <h3 className="text-2xl font-semibold mb-2">
            Select a video to view analysis
          </h3>
          <p className="text-muted-foreground max-w-md mb-6">
            Upload a cricket batting video and get AI-powered insights into your technique.
            Our advanced ML algorithms will analyze your footwork, balance, swing path, and more.
          </p>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Sparkles className="h-4 w-4" />
            <span>Powered by advanced AI analysis</span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

