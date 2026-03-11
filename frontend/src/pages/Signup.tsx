import { Check, Info, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { showToast } from '@/utils/toast'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'

interface PasswordRequirements {
  length: boolean
  uppercase: boolean
  lowercase: boolean
  number: boolean
  special: boolean
}

function calculatePasswordStrength(password: string): number {
  let score = 0
  if (password.length >= 8) score += 20
  if (password.length >= 12) score += 10
  if (password.length >= 16) score += 10
  if (/[A-Z]/.test(password)) score += 15
  if (/[a-z]/.test(password)) score += 15
  if (/[0-9]/.test(password)) score += 15
  if (/[!@#$%^&*]/.test(password)) score += 15
  return score
}

function checkPasswordRequirements(password: string): PasswordRequirements {
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*]/.test(password),
  }
}

export default function Signup() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [isCheckingSetup, setIsCheckingSetup] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [requirements, setRequirements] = useState<PasswordRequirements>({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false,
  })
  const [passwordStrength, setPasswordStrength] = useState(0)

  useEffect(() => {
    const checkSetup = async () => {
      try {
        const setupResponse = await fetch('/auth/check-setup', {
          credentials: 'include',
        })
        const setupData = await setupResponse.json()
        if (setupData.needs_setup) {
          navigate('/setup', { replace: true })
          return
        }
      } catch {
      } finally {
        setIsCheckingSetup(false)
      }
    }
    checkSetup()
  }, [navigate])

  useEffect(() => {
    const reqs = checkPasswordRequirements(formData.password)
    setRequirements(reqs)
    setPasswordStrength(calculatePasswordStrength(formData.password))
  }, [formData.password])

  const allRequirementsMet = Object.values(requirements).every(Boolean)
  const passwordsMatch = formData.password === formData.confirmPassword
  const allFieldsFilled = Object.values(formData).every((v) => v.trim() !== '')
  const canSubmit = allRequirementsMet && passwordsMatch && allFieldsFilled

  const getStrengthLabel = () => {
    if (passwordStrength >= 80) return { label: 'Strong', color: 'text-green-500' }
    if (passwordStrength >= 50) return { label: 'Medium', color: 'text-yellow-500' }
    if (passwordStrength > 0) return { label: 'Weak', color: 'text-red-500' }
    return { label: '', color: '' }
  }

  const strengthInfo = getStrengthLabel()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!canSubmit) return

    setIsLoading(true)
    setError(null)

    try {
      const csrfResponse = await fetch('/auth/csrf-token', {
        credentials: 'include',
      })
      const csrfData = await csrfResponse.json()

      const form = new FormData()
      form.append('username', formData.username)
      form.append('email', formData.email)
      form.append('password', formData.password)
      form.append('confirm_password', formData.confirmPassword)
      form.append('csrf_token', csrfData.csrf_token)

      const response = await fetch('/auth/signup', {
        method: 'POST',
        body: form,
        credentials: 'include',
      })

      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        setError('Signup failed. Please try again.')
        return
      }

      const data = await response.json()
      if (data.status === 'error') {
        setError(data.message || 'Signup failed. Please try again.')
        if (data.redirect) {
          navigate(data.redirect)
        }
        return
      }

      showToast.success('Account created successfully', 'system')
      navigate(data.redirect || '/broker-setup')
    } catch {
      setError('Signup failed. Please check your connection and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const RequirementItem = ({ met, children }: { met: boolean; children: React.ReactNode }) => (
    <div
      className={cn(
        'flex items-center gap-2 text-sm py-1 transition-colors',
        met ? 'text-green-500' : 'text-muted-foreground'
      )}
    >
      <Check className={cn('h-4 w-4', met ? 'opacity-100' : 'opacity-0')} />
      <span>{children}</span>
    </div>
  )

  if (isCheckingSetup) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center py-12 px-4">
      <div className="container max-w-6xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center">
          <div className="space-y-6 lg:pr-8">
            <div className="space-y-4">
              <h1 className="text-4xl lg:text-5xl font-bold leading-tight">
                Create Your <span className="text-primary">Account</span>
              </h1>
              <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
                Set up your OpenAlgo user account. After signup, you will configure your broker
                API credentials to connect and start trading.
              </p>
            </div>

            <Alert>
              <Info className="h-5 w-5" />
              <AlertDescription>
                <strong className="block mb-1">Broker Setup Required</strong>
                You will be prompted to enter your broker API key, secret, and redirect URL after
                creating your account.
              </AlertDescription>
            </Alert>
          </div>

          <div className="w-full">
            <Card>
              <CardContent className="p-6 lg:p-8">
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      name="username"
                      type="text"
                      placeholder="Choose a username"
                      value={formData.username}
                      onChange={handleInputChange}
                      required
                      disabled={isLoading}
                      autoComplete="username"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="Enter your email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="Create a strong password"
                      value={formData.password}
                      onChange={handleInputChange}
                      required
                      disabled={isLoading}
                      autoComplete="new-password"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirm Password</Label>
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      placeholder="Confirm your password"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      required
                      disabled={isLoading}
                      autoComplete="new-password"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Password Strength</Label>
                      <span className={cn('text-sm font-medium', strengthInfo.color)}>
                        {strengthInfo.label}
                      </span>
                    </div>
                    <Progress value={passwordStrength} className="h-2" />
                    <div className="space-y-1">
                      <RequirementItem met={requirements.length}>
                        At least 8 characters
                      </RequirementItem>
                      <RequirementItem met={requirements.uppercase}>
                        At least 1 uppercase letter
                      </RequirementItem>
                      <RequirementItem met={requirements.lowercase}>
                        At least 1 lowercase letter
                      </RequirementItem>
                      <RequirementItem met={requirements.number}>
                        At least 1 number
                      </RequirementItem>
                      <RequirementItem met={requirements.special}>
                        At least 1 special character (!@#$%^&*)
                      </RequirementItem>
                    </div>
                  </div>

                  {!passwordsMatch && formData.confirmPassword && (
                    <Alert variant="destructive">
                      <AlertDescription>Passwords do not match</AlertDescription>
                    </Alert>
                  )}

                  {error && (
                    <Alert variant="destructive">
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  <Button type="submit" className="w-full" disabled={!canSubmit || isLoading}>
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating account...
                      </>
                    ) : (
                      'Create Account'
                    )}
                  </Button>

                  <div className="text-center text-sm text-muted-foreground">
                    Already have an account?{' '}
                    <Link to="/login" className="text-primary hover:underline">
                      Sign in
                    </Link>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
