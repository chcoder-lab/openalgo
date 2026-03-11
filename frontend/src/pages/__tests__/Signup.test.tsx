import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import Signup from '../Signup'

const mockFetch = (url: RequestInfo | URL, init?: RequestInit) => {
  const method = (init?.method || 'GET').toUpperCase()
  if (url === '/auth/check-setup') {
    return Promise.resolve(
      new Response(JSON.stringify({ needs_setup: false }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      })
    )
  }
  if (url === '/auth/csrf-token') {
    return Promise.resolve(
      new Response(JSON.stringify({ csrf_token: 'csrf' }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      })
    )
  }
  if (url === '/auth/signup' && method === 'POST') {
    return Promise.resolve(
      new Response(JSON.stringify({ status: 'success', redirect: '/broker-setup' }), {
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
}

// @ts-expect-error: test override
global.fetch = vi.fn(mockFetch)

describe('Signup', () => {
  it('submits signup form', async () => {
    render(
      <MemoryRouter>
        <Signup />
      </MemoryRouter>
    )

    await waitFor(() => expect(screen.getByText('Create Account')).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'user1' } })
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'user1@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'StrongPass1!' } })
    fireEvent.change(screen.getByLabelText('Confirm Password'), {
      target: { value: 'StrongPass1!' },
    })

    fireEvent.click(screen.getByRole('button', { name: 'Create Account' }))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/auth/signup', expect.any(Object))
    })
  })
})
