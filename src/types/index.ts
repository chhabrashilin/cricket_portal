export interface Video {
  id: number
  filename: string
  file_path: string
  user_id: number | null
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at?: string
}

export interface Weakness {
  category: string
  severity: 'low' | 'medium' | 'high'
  description: string
  frame_timestamp?: number
  confidence: number
  score?: number
}

export interface Strength {
  category: string
  description: string
  score: number
}

export interface Analysis {
  id: number
  video_id: number
  overall_score: number
  weaknesses: Weakness[]
  strengths: Strength[]
  recommendations: string[]
  detailed_metrics: {
    analyses?: Record<string, any>
    raw_metrics?: Record<string, any>
    video_metadata?: Record<string, any>
  }
  created_at: string
}

