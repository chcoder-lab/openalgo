import { Info, Search } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface SearchResult {
  symbol: string
  name: string
  exchange: string
  token: string
  expiry?: string
  strike?: number
}

const EXCHANGES = [
  { value: 'EQUITY', label: 'EQUITY - US Equities' },
  { value: 'OPTIONS', label: 'OPTIONS - Equity Options' },
  { value: 'FUTURES', label: 'FUTURES - Futures' },
  { value: 'FUTURES_OPTION', label: 'FUTURES_OPTION - Futures Options' },
  { value: 'CRYPTO', label: 'CRYPTO - Cryptocurrency' },
]

export default function Token() {
  const navigate = useNavigate()
  const [symbol, setSymbol] = useState('')
  const [exchange, setExchange] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [showResults, setShowResults] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [symbolError, setSymbolError] = useState('')

  const inputWrapperRef = useRef<HTMLDivElement>(null)

  // Debounced search for autocomplete
  const performAutocompleteSearch = useCallback(
    async (query: string, exch: string) => {
      if (query.length < 2) {
        setSearchResults([])
        setShowResults(false)
        return
      }

      setIsLoading(true)
      try {
        const params = new URLSearchParams()
        if (query) params.append('q', query)
        if (exch) params.append('exchange', exch)

        const response = await fetch(`/search/api/search?${params}`, {
          credentials: 'include',
        })
        const data = await response.json()
        setSearchResults((data.results || []).slice(0, 10))
        setShowResults(true)
      } catch (error) {
        setSearchResults([])
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  // Debounced input handler
  useEffect(() => {
    const timer = setTimeout(() => {
      if (symbol.length >= 2) {
        performAutocompleteSearch(symbol, exchange)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [symbol, exchange, performAutocompleteSearch])

  // Click-outside handler to close dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (inputWrapperRef.current && !inputWrapperRef.current.contains(e.target as Node)) {
        setShowResults(false)
      }
    }
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setShowResults(false)
    setSymbolError('')

    if (!symbol) {
      setSymbolError('Required - enter a search term')
      return
    }

    if (!exchange) {
      return
    }

    const params = new URLSearchParams()
    if (symbol) params.append('symbol', symbol)
    if (exchange) params.append('exchange', exchange)

    navigate(`/search?${params.toString()}`)
  }

  const handleResultClick = (result: SearchResult) => {
    setSymbol(result.symbol)
    setExchange(result.exchange)
    setShowResults(false)
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl lg:text-5xl font-bold mb-4">Symbol Search</h1>
        <p className="text-lg text-muted-foreground">
          Search for symbols across different exchanges to get detailed information
        </p>
      </div>

      {/* Search Form */}
      <Card className="mb-6">
        <CardContent className="p-6 lg:p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Symbol Search */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label htmlFor="symbol">Symbol, Name, or Token</Label>
                <span
                  className={`text-xs ${symbolError ? 'text-red-500' : 'text-muted-foreground'}`}
                >
                  {symbolError || '(Required)'}
                </span>
              </div>
              <div className="relative" ref={inputWrapperRef}>
                <Input
                  id="symbol"
                  type="text"
                  placeholder="e.g., AAPL, TSLA, SPX"
                  value={symbol}
                  onChange={(e) => {
                    setSymbol(e.target.value)
                    setSymbolError('')
                  }}
                  onFocus={() => {
                    if (symbol.length >= 2) {
                      setShowResults(true)
                    }
                  }}
                  autoComplete="off"
                />
                {isLoading && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  </div>
                )}

                {/* Autocomplete Results */}
                {showResults && searchResults.length > 0 && (
                  <div className="absolute z-50 w-full mt-1 bg-background border rounded-lg shadow-lg max-h-96 overflow-y-auto">
                    {searchResults.map((result, index) => (
                      <div
                        key={index}
                        className="p-3 border-b last:border-b-0 hover:bg-muted cursor-pointer"
                        onClick={() => handleResultClick(result)}
                      >
                        <div className="flex justify-between items-start gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold truncate">{result.symbol}</div>
                            <div className="text-sm text-muted-foreground truncate">
                              {result.name}
                            </div>
                            <div className="text-xs text-muted-foreground font-mono">
                              Token: {result.token}
                            </div>
                          </div>
                          <span className="shrink-0 bg-primary text-primary-foreground px-3 py-1 rounded-full text-xs font-semibold">
                            {result.exchange}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {showResults && searchResults.length === 0 && symbol.length >= 2 && !isLoading && (
                  <div className="absolute z-50 w-full mt-1 bg-background border rounded-lg shadow-lg p-8 text-center">
                    <Search className="h-12 w-12 mx-auto text-muted-foreground/50 mb-3" />
                    <div className="font-medium">No results found</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Try a different search term
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Exchange Select */}
            <div className="space-y-2">
              <Label htmlFor="exchange">Exchange</Label>
              <Select value={exchange} onValueChange={setExchange}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Exchange" />
                </SelectTrigger>
                <SelectContent>
                  {EXCHANGES.map((ex) => (
                    <SelectItem key={ex.value} value={ex.value}>
                      {ex.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Search Button */}
            <Button type="submit" className="w-full" size="lg">
              <Search className="mr-2 h-5 w-5" />
              Search Symbol
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Search Tips */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Search Tips</AlertTitle>
        <AlertDescription className="space-y-3 mt-2">
          <div>
            <div className="font-semibold mb-1">Stock Search:</div>
            <ul className="ml-2 space-y-0.5 text-sm">
              <li>
                By symbol: <code className="bg-muted px-2 py-0.5 rounded">AAPL</code>,{' '}
                <code className="bg-muted px-2 py-0.5 rounded">TSLA</code>
              </li>
              <li>
                By company name:{' '}
                <code className="bg-muted px-2 py-0.5 rounded">Apple Inc</code>
              </li>
              <li>
                By token number: <code className="bg-muted px-2 py-0.5 rounded">12345</code>
              </li>
            </ul>
          </div>
          <div>
            <div className="font-semibold mb-1">Options & Futures:</div>
            <ul className="ml-2 space-y-0.5 text-sm">
              <li>
                Select <strong>OPTIONS</strong> exchange for equity options
              </li>
              <li>
                Select <strong>FUTURES</strong> exchange for futures contracts
              </li>
              <li>
                Select <strong>CRYPTO</strong> exchange for cryptocurrency
              </li>
            </ul>
          </div>
          <div className="text-xs text-muted-foreground mt-2">
            <strong>Tip:</strong> Select the appropriate exchange (EQUITY for stocks, OPTIONS for options) for accurate results
          </div>
        </AlertDescription>
      </Alert>
    </div>
  )
}
