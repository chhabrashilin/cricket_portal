'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle2, TrendingUp, Target, BarChart3, Activity } from 'lucide-react'
import { Analysis, Weakness, Strength } from '@/types'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Cell } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'

interface AnalysisResultsProps {
  analysis: Analysis
}

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4']

export default function AnalysisResults({ analysis }: AnalysisResultsProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20'
      case 'medium':
        return 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20'
      case 'low':
        return 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20'
      default:
        return 'bg-muted text-muted-foreground border-border'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400'
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getScoreGradient = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-600'
    if (score >= 60) return 'from-yellow-500 to-orange-600'
    return 'from-red-500 to-rose-600'
  }

  // Prepare data for charts
  const categoryScores = analysis.detailed_metrics?.analyses
    ? Object.entries(analysis.detailed_metrics.analyses).map(([category, data]: [string, any]) => ({
        category: category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        score: Math.round(data.score || 0),
        fullMark: 100
      }))
    : []

  const radarData = categoryScores.map(item => ({
    category: item.category.length > 12 ? item.category.substring(0, 12) + '...' : item.category,
    score: item.score,
    fullMark: 100
  }))

  const overallScore = Math.round(analysis.overall_score)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Overall Score Card */}
      <Card className="overflow-hidden border-2">
        <div className={cn(
          "relative bg-gradient-to-br p-6 text-white",
          getScoreGradient(overallScore)
        )}>
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-2xl font-bold">Analysis Complete</h2>
              <Activity className="h-6 w-6 opacity-80" />
            </div>
            <div className="flex items-baseline gap-2">
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="text-6xl font-bold"
              >
                {overallScore}
              </motion.span>
              <span className="text-2xl opacity-80">/ 100</span>
            </div>
            <p className="text-sm opacity-90 mt-2">
              Overall batting technique score
            </p>
          </div>
          <div className="absolute inset-0 bg-black/10" />
        </div>
      </Card>

      {/* Charts Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Performance Metrics
          </CardTitle>
          <CardDescription>
            Detailed breakdown of your batting technique across different aspects
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="bar" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="bar">Bar Chart</TabsTrigger>
              <TabsTrigger value="radar">Radar Chart</TabsTrigger>
            </TabsList>
            <TabsContent value="bar" className="mt-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryScores} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="category"
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    tick={{ fill: 'currentColor', fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: 'currentColor', fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--popover))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: 'var(--radius)',
                    }}
                  />
                  <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                    {categoryScores.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </TabsContent>
            <TabsContent value="radar" className="mt-6">
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid className="stroke-muted" />
                  <PolarAngleAxis
                    dataKey="category"
                    tick={{ fill: 'currentColor', fontSize: 11 }}
                    className="text-muted-foreground"
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 100]}
                    tick={{ fill: 'currentColor', fontSize: 11 }}
                    className="text-muted-foreground"
                  />
                  <Radar
                    name="Score"
                    dataKey="score"
                    stroke="#0ea5e9"
                    fill="#0ea5e9"
                    fillOpacity={0.6}
                    strokeWidth={2}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--popover))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: 'var(--radius)',
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Weaknesses */}
      {analysis.weaknesses.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="border-destructive/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                Identified Weaknesses
              </CardTitle>
              <CardDescription>
                Areas that need improvement in your batting technique
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysis.weaknesses.map((weakness: Weakness, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + index * 0.05 }}
                    className={cn(
                      "p-4 rounded-lg border-2 transition-all hover:shadow-md",
                      getSeverityColor(weakness.severity)
                    )}
                  >
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div className="font-semibold capitalize text-sm">
                        {weakness.category.replace('_', ' ')}
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <Badge variant={weakness.severity === 'high' ? 'destructive' : weakness.severity === 'medium' ? 'warning' : 'outline'}>
                          {weakness.severity.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {Math.round(weakness.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-sm leading-relaxed mb-2">{weakness.description}</p>
                    {weakness.score !== undefined && (
                      <div className="flex items-center gap-2 mt-3">
                        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${weakness.score}%` }}
                            transition={{ delay: 0.2 + index * 0.05, duration: 0.5 }}
                            className={cn(
                              "h-full rounded-full",
                              weakness.severity === 'high' ? 'bg-red-500' :
                              weakness.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                            )}
                          />
                        </div>
                        <span className="text-xs font-medium min-w-[3rem] text-right">
                          {weakness.score.toFixed(0)}/100
                        </span>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Strengths */}
      {analysis.strengths.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-green-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600 dark:text-green-400">
                <CheckCircle2 className="h-5 w-5" />
                Strengths
              </CardTitle>
              <CardDescription>
                Areas where your technique excels
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {analysis.strengths.map((strength: Strength, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 + index * 0.05 }}
                    className="p-4 rounded-lg bg-green-500/10 border border-green-500/20 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-semibold capitalize text-sm text-green-700 dark:text-green-300">
                        {strength.category.replace('_', ' ')}
                      </div>
                      <Badge variant="success" className="text-xs">
                        {strength.score.toFixed(0)}/100
                      </Badge>
                    </div>
                    <p className="text-sm text-green-600 dark:text-green-400 leading-relaxed">
                      {strength.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Recommendations
              </CardTitle>
              <CardDescription>
                Actionable steps to improve your batting technique
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysis.recommendations.map((recommendation: string, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.05 }}
                    className="flex items-start gap-3 p-4 rounded-lg bg-primary/5 border border-primary/20 hover:bg-primary/10 transition-colors group"
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                        <TrendingUp className="h-4 w-4 text-primary" />
                      </div>
                    </div>
                    <p className="text-sm leading-relaxed flex-1 pt-1">
                      {recommendation}
                    </p>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  )
}
