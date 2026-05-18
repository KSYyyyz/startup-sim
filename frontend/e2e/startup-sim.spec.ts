import { expect, test } from '@playwright/test';

test('creates a session and submits one turn', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('NimbusAI')).toBeVisible();
  await expect(page.getByText('现金流可支撑时间')).toBeVisible();
  await expect(page.getByText('核心矛盾')).toBeVisible();
  await expect(page.getByLabel('竞品态势')).toBeVisible();
  await expect(page.locator('body')).not.toContainText(/跑道|Runway/);

  if ((page.viewportSize()?.width ?? 0) <= 640) {
    await page.getByLabel('移动端本回合指令').fill('花10万研发产品');
    await page.getByRole('button', { name: '执行', exact: true }).click();
  } else {
    await page.getByLabel('本回合指令', { exact: true }).fill('花10万研发产品');
    await page.getByRole('button', { name: '执行回合' }).click();
  }

  await expect(page.getByText('第2月', { exact: true })).toBeVisible();
  await expect(page.getByText('回合结果')).toBeVisible();
  await expect(page.getByText('董事会反馈')).toBeVisible();
  await expect(page.getByLabel('竞品态势')).toBeVisible();
  await expect(page.locator('body')).not.toContainText(/跑道|Runway/);
});

test('loads detailed advice only after opening advice', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('输入「建议」查看详情')).toBeVisible();
  await page.getByRole('button', { name: '建议', exact: true }).click();

  await expect(page.getByText('建议详情')).toBeVisible();
  await expect(page.locator('code').first()).toBeVisible();
});
