import { test, expect } from '@playwright/test';

test.describe('AI Storybook UI', () => {
  test('loads setup screen', async ({ page }) => {
    await page.goto('/');

    // Wait for components to load and setup screen to be active
    await page.waitForSelector('#setup-screen', { state: 'visible' });
    await expect(page.locator('#setup-screen')).toBeVisible();
    await expect(page.locator('#setup-screen h2')).toHaveText(/Create Your Story/);
  });

  test('generate story flow (headed)', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#setup-screen', { state: 'visible' });

    await page.fill('#story-prompt', 'A brave squirrel time-travels to save the forest\'s seasons.');
    await page.selectOption('#age-group', '7-10');
    await page.selectOption('#genre', 'adventure');
    await page.selectOption('#art-style', 'watercolor');
    await page.fill('#num-scenes', '5');
    await page.fill('#character-count', '2');

    const responsePromise = page.waitForResponse(resp =>
      resp.url().endsWith('/api/generate-story') && resp.status() === 200
    );

    await page.click('#generate-btn');

    const resp = await responsePromise;
    const json = await resp.json();
    expect(json).toHaveProperty('story_id');

    // Optionally wait for some UI update that indicates generation started
    // e.g., loading overlay or next screen elements
    await page.waitForTimeout(500); // brief pause to observe in headed mode
  });
});

