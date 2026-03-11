import { Info, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { showToast } from '@/utils/toast'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { webClient } from '@/api/client'

interface BrokerCredentials {
  broker_api_key: string
  broker_api_key_raw_length: number
  broker_api_secret: string
  broker_api_secret_raw_length: number
  redirect_url: string
  current_broker: string
  valid_brokers: string[]
}

export default function BrokerSetup() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [credentials, setCredentials] = useState<BrokerCredentials | null>(null)
  const [selectedBroker, setSelectedBroker] = useState('')
  const [brokerApiKey, setBrokerApiKey] = useState('')
  const [brokerApiSecret, setBrokerApiSecret] = useState('')
  const [redirectUrl, setRedirectUrl] = useState('')

  useEffect(() => {
    const init = async () => {
      try {
        const sessionResponse = await fetch('/auth/session-status', {
          credentials: 'include',
        })
        const sessionData = await sessionResponse.json()
        if (!sessionData?.authenticated) {
          navigate('/login', { replace: true })
          return
        }

        const response = await webClient.get<{ status: string; data: BrokerCredentials }>(
          '/api/broker/credentials'
        )
        const data = response.data.data
        setCredentials(data)
        setSelectedBroker(data.current_broker || '')
        setRedirectUrl(data.redirect_url || '')
      } catch (err) {
        showToast.error('Failed to load broker credentials', 'system')
      } finally {
        setIsLoading(false)
      }
    }

    init()
  }, [navigate])

  const getRedirectUrl = (broker: string): string => {
    const currentUrl = credentials?.redirect_url || 'http://127.0.0.1:5000'
    const host = currentUrl.split('/').slice(0, 3).join('/')
    return `${host}/${broker}/callback`
  }

  const handleBrokerChange = (value: string) => {
    setSelectedBroker(value)
    setRedirectUrl(getRedirectUrl(value))
  }

  const handleSave = async () => {
    if (!selectedBroker) {
      showToast.error('Please select a broker', 'system')
      return
    }

    setIsSaving(true)
    try {
      const formData = new FormData()
      if (brokerApiKey) formData.append('broker_api_key', brokerApiKey)
      if (brokerApiSecret) formData.append('broker_api_secret', brokerApiSecret)
      if (redirectUrl) formData.append('redirect_url', redirectUrl)

      const response = await webClient.post('/api/broker/credentials', formData)

      if (response.data?.status === 'success') {
        showToast.success('Broker credentials saved.', 'system')
        setBrokerApiKey('')
        setBrokerApiSecret('')
        setCredentials((prev) =>
          prev
            ? {
                ...prev,
                current_broker: selectedBroker,
                redirect_url: redirectUrl || prev.redirect_url,
                broker_api_key: brokerApiKey
                  ? `${brokerApiKey.slice(0, 6)}${'*'.repeat(Math.max(0, brokerApiKey.length - 6))}`
                  : prev.broker_api_key,
                broker_api_key_raw_length: brokerApiKey
                  ? brokerApiKey.length
                  : prev.broker_api_key_raw_length,
                broker_api_secret: brokerApiSecret
                  ? `${brokerApiSecret.slice(0, 4)}${'*'.repeat(Math.max(0, brokerApiSecret.length - 4))}`
                  : prev.broker_api_secret,
                broker_api_secret_raw_length: brokerApiSecret
                  ? brokerApiSecret.length
                  : prev.broker_api_secret_raw_length,
              }
            : prev
        )
        return
      }

      showToast.error(response.data?.message || 'Failed to save broker credentials', 'system')
    } catch (err: any) {
      showToast.error(err?.response?.data?.message || 'Failed to save broker credentials', 'system')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center py-12 px-4">
      <div className="container max-w-4xl">
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>Broker API Credentials</CardTitle>
            <CardDescription>
              Enter your broker API key, secret token, and redirect URL to connect your account.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert>
              <Info className="h-5 w-5" />
              <AlertTitle>Broker Setup</AlertTitle>
              <AlertDescription>
                Credentials are saved per user and take effect immediately.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label>Select Broker</Label>
              <Select value={selectedBroker} onValueChange={handleBrokerChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a broker" />
                </SelectTrigger>
                <SelectContent>
                  {credentials?.valid_brokers.map((broker) => (
                    <SelectItem key={broker} value={broker}>
                      {broker.charAt(0).toUpperCase() + broker.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Broker API Key</Label>
                <Input
                  placeholder="Enter broker API key"
                  value={brokerApiKey}
                  onChange={(e) => setBrokerApiKey(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Broker API Secret</Label>
                <Input
                  placeholder="Enter broker API secret"
                  value={brokerApiSecret}
                  onChange={(e) => setBrokerApiSecret(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Redirect URL</Label>
              <Input
                placeholder="https://your-domain/broker/callback"
                value={redirectUrl}
                onChange={(e) => setRedirectUrl(e.target.value)}
              />
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
              <Button variant="outline" onClick={() => navigate('/login')}>
                Back to Login
              </Button>
              <div className="flex flex-col gap-3 sm:flex-row">
                <Button variant="secondary" onClick={() => navigate('/broker')}>
                  Continue to Broker Login
                </Button>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Credentials'
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
