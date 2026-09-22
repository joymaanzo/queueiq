import { test, expect } from '@playwright/test'

const apiUrl = 'http://localhost:8000'

async function openApp(page: import('@playwright/test').Page) {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Clinic wait-time made clearer.' })).toBeVisible()
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
