import { test, expect } from '@playwright/test';
import path from 'node:path';

test('generated architecture editor renders nodes, edges, and endpoint panel', async ({ page }) => {
  const htmlPath = path.resolve('tmp/architecture-editor.html');
  const errors = [] as string[];
  page.on('pageerror', err => errors.push(err.message));
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  await page.goto(`file://${htmlPath}`);
  await expect(page.locator('.node')).not.toHaveCount(0);
  await expect(page.locator('svg path')).not.toHaveCount(0);
  await page.locator('.node').first().click();
  await expect(page.locator('#panel')).toBeVisible();
  await expect(page.getByRole('button', { name: /EXPORT DATA/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /EXPORT CHANGES/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /EXPORT ALL STATES/i })).toBeVisible();
  expect(errors).toEqual([]);
});
