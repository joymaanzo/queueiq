import { test, expect } from '@playwright/test'

const apiUrl = 'http://localhost:8000'

async function openApp(page: import('@playwright/test').Page) {
  let healthOk = false
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const response = await fetch(`${apiUrl}/health`)
      if (response.ok) {
        healthOk = true
        break
      }
    } catch {
      // Backend not ready yet.
    }
    await page.waitForTimeout(1000)
  }

  if (!healthOk) {
    throw new Error('Backend health check failed after 30 seconds')
  }

  await page.goto('http://localhost:8000')
  await page.waitForLoadState('networkidle')
}

test('loads frontend and verifies health endpoint', async ({ page, request }) => {
  await openApp(page)
  const response = await request.get(`${apiUrl}/health`)
  expect(response.status()).toBe(200)
  expect((await response.json()).status).toBe('ok')
})

test('selects a clinic from the dropdown', async ({ page }) => {
  await openApp(page)
  const clinic = page.getByLabel('Clinic')
  await expect(clinic).toBeEnabled()
  await expect(clinic.locator('option')).toHaveCount(4)
  await clinic.selectOption('2')
  await expect(clinic).toHaveValue('2')
})

test('submits a prediction successfully', async ({ page }) => {
  await openApp(page)
  await expect(page.getByLabel('Clinic')).toBeEnabled()
  await page.getByLabel('Current queue length (optional)').fill('5')
  const responsePromise = page.waitForResponse((response) =>
    response.url().endsWith('/predict-wait-time') && response.request().method() === 'POST',
  )
  await page.getByRole('button', { name: 'Predict wait time' }).click()
  const response = await responsePromise
  expect(response.status()).toBe(200)
  expect((await response.json()).prediction_id).toBeGreaterThan(0)
  await expect(page.getByText('minutes', { exact: false }).first()).toBeVisible()
})
