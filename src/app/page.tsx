'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import VideoUpload from '@/components/VideoUpload'
import VideoList from '@/components/VideoList'
import AnalysisResults from '@/components/AnalysisResults'
import VideoPlayer from '@/components/VideoPlayer'
import EmptyState from '@/components/EmptyState'
import { useToast } from '@/hooks/use-toast'
import { Video, Analysis } from '@/types'

export default function Home() {
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const { toast } = useToast()

  const handleVideoUploaded = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  const handleVideoSelected = async (video: Video) => {
    setSelectedVideo(video)
    
    // Fetch analysis if available
    if (video.analysis_status === 'completed') {
      try {
        const response = await fetch(`http://localhost:8000/api/videos/${video.id}/analysis`)
        if (response.ok) {
          const analysisData = await response.json()
          setAnalysis(analysisData)
        }
      } catch (error) {
        console.error('Error fetching analysis:', error)
      }
    } else {
      setAnalysis(null)
    }
  }

  const handleAnalyze = async (videoId: number) => {
    try {
      setIsAnalyzing(true)
      const response = await fetch(`http://localhost:8000/api/videos/${videoId}/analyze`, {
        method: 'POST',
      })
      
      if (response.ok) {
        const analysisData = await response.json()
        setAnalysis(analysisData)
        setRefreshTrigger(prev => prev + 1)
        
        // Update selected video status
        if (selectedVideo) {
          setSelectedVideo({ ...selectedVideo, analysis_status: 'completed' })
        }
        
        toast({
          title: "Analysis complete!",
          description: `Your video has been analyzed. Overall score: ${analysisData.overall_score.toFixed(1)}/100`,
        })
      } else {
        throw new Error('Analysis failed')
      }
    } catch (error) {
      console.error('Error analyzing video:', error)
      toast({
        title: "Analysis failed",
        description: "Error analyzing video. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 lg:py-12">
        {/* Hero Section */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12 lg:mb-16"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring" }}
            className="inline-block mb-6"
          >
            <div className="text-6xl mb-4">🏏</div>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent"
          >
            Cricket Batting Analyzer
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed"
          >
            Revolutionary AI-powered analysis platform that identifies weaknesses in your batting technique
            and provides actionable recommendations to improve your game.
          </motion.p>
        </motion.header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* Left Column - Upload & Video List */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-1 space-y-6"
          >
            <VideoUpload onUploaded={handleVideoUploaded} />
            <VideoList
              onVideoSelect={handleVideoSelected}
              selectedVideoId={selectedVideo?.id}
              refreshTrigger={refreshTrigger}
            />
          </motion.div>

          {/* Right Column - Video Player & Analysis */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-2 space-y-6"
          >
            {selectedVideo ? (
              <>
                <VideoPlayer
                  video={selectedVideo}
                  onAnalyze={handleAnalyze}
                  isAnalyzing={isAnalyzing}
                />

                {analysis && (
                  <AnalysisResults analysis={analysis} />
                )}
              </>
            ) : (
              <EmptyState />
            )}
          </motion.div>
        </div>
      </div>
    </main>
  )
}
