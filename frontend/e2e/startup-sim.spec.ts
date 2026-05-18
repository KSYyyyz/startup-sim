import { expect, test } from '@playwright/test';

test('creates a session and submits one turn', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('NimbusAI')).toBeVisible();
  await expect(page.getByLabel('当前剧本')).toBeVisible();
  await expect(page.getByText('难度：标准')).toBeVisible();
  await expect(page.getByLabel('公司指标').getByText('现金流可支撑时间', { exact: true })).toBeVisible();
  await expect(page.getByLabel('新手经营节奏')).toBeVisible();
  await expect(page.getByLabel('本月小目标')).toBeVisible();
  await expect(page.getByRole('heading', { name: '核心矛盾' })).toBeVisible();
  await expect(page.getByText('经营洞察')).toBeVisible();
  await expect(page.getByLabel('互动办公室场景')).toBeVisible();
  await expect(page.getByLabel('办公室操作台')).toBeVisible();
  await expect(page.getByLabel('办公室动态反馈')).not.toBeVisible();
  await expect(page.getByLabel('产品室状态')).toContainText('产品压力');
  if ((page.viewportSize()?.width ?? 0) <= 640) {
    await expect(page.getByRole('button', { name: '移动端执行' })).toBeDisabled();
    await expect(page.getByRole('button', { name: '移动端解释指令' })).toBeDisabled();
  } else {
    await expect(page.getByRole('button', { name: '解释指令', exact: true })).toBeDisabled();
  }
  const sideTabs = page.getByRole('tablist', { name: '右侧信息' });
  await sideTabs.getByRole('button', { name: '竞品', exact: true }).click();
  await expect(sideTabs.getByRole('button', { name: '竞品', exact: true })).toHaveClass(/active/);
  await page.locator('.competitor-response-button').first().click();
  await expect(page.locator('.prepared-action')).toBeVisible();
  await expect(page.locator('.prepared-action .action-tags small')).toHaveCount(2);
  if ((page.viewportSize()?.width ?? 0) <= 640) {
    await expect(page.getByLabel('移动端本回合指令')).not.toHaveValue('');
  } else {
    await expect(page.getByLabel('本回合指令', { exact: true })).not.toHaveValue('');
  }
  await sideTabs.getByRole('button', { name: '董事会', exact: true }).click();
  await expect(sideTabs.getByRole('button', { name: '董事会', exact: true })).toHaveClass(/active/);
  await expect(page.getByLabel('竞品态势')).not.toBeVisible();
  await expect(page.locator('body')).not.toContainText(/跑道|Runway/);

  await page.getByRole('button', { name: '产品室' }).click();
  await expect(page.getByText('产品打磨', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: '采用行动：产品打磨' }).click();
  const preparedAction = page.getByRole('article', { name: '已准备行动' });
  await expect(preparedAction).toContainText('产品打磨');
  await expect(preparedAction).toContainText('花10万研发产品');

  if ((page.viewportSize()?.width ?? 0) <= 640) {
    await expect(page.getByLabel('移动端本回合指令')).toHaveValue('花10万研发产品');
    await page.getByRole('button', { name: '移动端解释指令' }).click();
    await expect(page.getByLabel('AI 指令解释')).toContainText('产品研发');
    await page.getByRole('button', { name: '移动端执行' }).click();
  } else {
    await expect(page.getByLabel('本回合指令', { exact: true })).toHaveValue('花10万研发产品');
    await page.getByRole('button', { name: '解释指令' }).click();
    await expect(page.getByLabel('AI 指令解释')).toContainText('产品研发');
    await expect(page.getByLabel('AI 指令解释')).toContainText('TurnEngine');
    await page.getByRole('button', { name: '执行回合' }).click();
  }

  await expect(page.getByText('第2月', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: '月度战报' })).toBeVisible();
  await expect(page.getByLabel('回合结算')).toBeVisible();
  await expect(page.getByLabel('办公室月末变化')).toBeVisible();
  await expect(page.getByRole('heading', { name: '董事会反馈' })).toBeVisible();
  await sideTabs.getByRole('button', { name: '竞品', exact: true }).click();
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
