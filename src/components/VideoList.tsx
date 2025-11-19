'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Clock, CheckCircle2, Loader2, AlertCircle, FileVideo } from 'lucide-react'
import { Video } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

interface VideoListProps {
  onVideoSelect: (video: Video) => void
  selectedVideoId?: number
  refreshTrigger: number
}

export default function VideoList({ onVideoSelect, selectedVideoId, refreshTrigger }: VideoListProps) {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchVideos()
  }, [refreshTrigger])

  const fetchVideos = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('http://localhost:8000/api/videos')
      if (response.ok) {
        const data = await response.json()
        setVideos(data.sort((a: Video, b: Video) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ))
      } else {
        throw new Error('Failed to fetch videos')
      }
    } catch (error) {
      console.error('Error fetching videos:', error)
      setError('Failed to load videos. Please refresh the page.')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success" className="gap-1"><CheckCircle2 className="h-3 w-3" />Completed</Badge>
      case 'processing':
        return <Badge variant="warning" className="gap-1"><Loader2 className="h-3 w-3 animate-spin" />Processing</Badge>
      case 'failed':
        return <Badge variant="destructive" className="gap-1"><AlertCircle className="h-3 w-3" />Failed</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileVideo className="h-5 w-5" />
          Your Videos
        </CardTitle>
        <CardDescription>
          {videos.length > 0 ? `${videos.length} video${videos.length !== 1 ? 's' : ''} uploaded` : 'No videos yet'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-20 w-full" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <AlertCircle className="h-12 w-12 text-destructive mb-4" />
            <p className="text-sm text-destructive mb-2">{error}</p>
            <button
              onClick={fetchVideos}
              className="text-sm text-primary hover:underline"
            >
              Try again
            </button>
          </div>
        ) : videos.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-12 text-center"
          >
            <div className="rounded-full bg-muted p-4 mb-4">
              <FileVideo className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-sm font-medium mb-1">No videos uploaded yet</p>
            <p className="text-xs text-muted-foreground">
              Upload your first video to get started with analysis
            </p>
          </motion.div>
        ) : (
          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
            <AnimatePresence mode="popLayout">
              {videos.map((video, index) => (
                <motion.div
                  key={video.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => onVideoSelect(video)}
                  className={cn(
                    "group relative p-4 rounded-lg border-2 cursor-pointer transition-all duration-200",
                    "hover:border-primary/50 hover:shadow-md hover:scale-[1.02]",
                    "active:scale-[0.98]",
                    selectedVideoId === video.id
                      ? "border-primary bg-primary/5 shadow-md"
                      : "border-border bg-card hover:bg-accent/50"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className={cn(
                      "flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
                      selectedVideoId === video.id
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary"
                    )}>
                      <Play className="h-5 w-5" fill="currentColor" />
                    </div>
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <p className="font-medium text-sm leading-tight line-clamp-2">
                          {video.filename}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 flex-wrap">
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <Clock className="h-3.5 w-3.5" />
                          <span>{formatDate(video.created_at)}</span>
                        </div>
                        {getStatusBadge(video.analysis_status)}
                      </div>
                    </div>
                  </div>
                  {selectedVideoId === video.id && (
                    <motion.div
                      layoutId="selectedIndicator"
                      className="absolute inset-0 border-2 border-primary rounded-lg pointer-events-none"
                      initial={false}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
