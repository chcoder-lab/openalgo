import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import BrokerSetup from '../BrokerSetup'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(async () => ({
    data: {
      status: 'success',
      data: {
        broker_api_key: '',
        broker_api_key_raw_length: 0,
        broker_api_secret: '',
        broker_api_secret_raw_length: 0,
        broker_api_key_market: '',
        broker_api_key_market_raw_length: 0,
        broker_api_secret_market: '',
        broker_api_secret_market_raw_length: 0,
        redirect_url: 'http://127.0.0.1:5000/zerodha/callback',
        current_broker: 'zerodha',
        valid_brokers: ['zerodha'],
      },
    },
  })),
  mockPost: vi.fn(async () => ({ data: { status: 'success' } })),
}))

vi.mock('@/api/client', () => ({
  webClient: {
    get: mockGet,
    post: mockPost,
  },
}))

// @ts-expect-error: test override
global.fetch = vi.fn((url: RequestInfo | URL) => {
  if (url === '/auth/session-status') {
    return Promise.resolve(
      new Response(JSON.stringify({ status: 'success', authenticated: true }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      })
    )
  }
  return Promise.resolve(
    new Response(JSON.stringify({ status: 'error' }), {
      status: 400,
      headers: { 'content-type': 'application/json' },
    })
  )
})

describe('BrokerSetup', () => {
  it('renders broker credential fields', async () => {
    render(
      <MemoryRouter>
        <BrokerSetup />
      </MemoryRouter>
    )

    await waitFor(() => expect(screen.getByText('Broker API Credentials')).toBeInTheDocument())

    expect(screen.getByPlaceholderText('Enter broker API key')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter broker API secret')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('https://your-domain/broker/callback')).toBeInTheDocument()
  })
})
