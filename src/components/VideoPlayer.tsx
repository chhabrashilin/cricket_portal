'use client'

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Pause, Loader2, AlertCircle } from 'lucide-react'
import { Video } from '@/types'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

interface VideoPlayerProps {
  video: Video
  onAnalyze: (videoId: number) => void
  isAnalyzing?: boolean
}

export default function VideoPlayer({ video, onAnalyze, isAnalyzing = false }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const videoElement = videoRef.current
    if (!videoElement) return

    const handleLoadStart = () => setIsLoading(true)
    const handleCanPlay = () => setIsLoading(false)
    const handleError = () => {
      setHasError(true)
      setIsLoading(false)
    }

    videoElement.addEventListener('loadstart', handleLoadStart)
    videoElement.addEventListener('canplay', handleCanPlay)
    videoElement.addEventListener('error', handleError)

    return () => {
      videoElement.removeEventListener('loadstart', handleLoadStart)
      videoElement.removeEventListener('canplay', handleCanPlay)
      videoElement.removeEventListener('error', handleError)
    }
  }, [])

  const togglePlay = () => {
    const videoElement = videoRef.current
    if (!videoElement) return

    if (isPlaying) {
      videoElement.pause()
    } else {
      videoElement.play()
    }
    setIsPlaying(!isPlaying)
  }

  const getStatusBadge = () => {
    switch (video.analysis_status) {
      case 'completed':
        return <Badge variant="success">Analysis Complete</Badge>
      case 'processing':
        return <Badge variant="warning" className="gap-1"><Loader2 className="h-3 w-3 animate-spin" />Processing</Badge>
      case 'failed':
        return <Badge variant="destructive">Analysis Failed</Badge>
      default:
        return <Badge variant="outline">Pending Analysis</Badge>
    }
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <CardTitle className="line-clamp-2 mb-2">{video.filename}</CardTitle>
            <CardDescription className="flex items-center gap-2">
              Uploaded {new Date(video.created_at).toLocaleDateString()}
            </CardDescription>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative aspect-video bg-black rounded-lg overflow-hidden group">
          {hasError ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-white p-6">
              <AlertCircle className="h-12 w-12 mb-4 text-destructive" />
              <p className="text-sm text-center">Failed to load video</p>
            </div>
          ) : (
            <>
              {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
                  <Loader2 className="h-8 w-8 text-white animate-spin" />
                </div>
              )}
              <video
                ref={videoRef}
                src={`http://localhost:8000/api/videos/${video.id}/video`}
                className="w-full h-full object-contain"
                controls
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {video.analysis_status === 'completed' && 'Ready for review'}
        </div>
        {video.analysis_status !== 'completed' && (
          <Button
            onClick={() => onAnalyze(video.id)}
            disabled={isAnalyzing || video.analysis_status === 'processing'}
            className="gap-2"
          >
            {isAnalyzing || video.analysis_status === 'processing' ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Analyze Video
              </>
            )}
          </Button>
        )}
      </CardFooter>
    </Card>
  )
}

