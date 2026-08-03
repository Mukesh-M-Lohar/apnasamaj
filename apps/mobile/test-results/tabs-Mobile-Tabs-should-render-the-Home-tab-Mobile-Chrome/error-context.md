# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tabs.spec.ts >> Mobile Tabs >> should render the Home tab
- Location: tests/tabs.spec.ts:18:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Profile').first()
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 15000ms
  - waiting for locator('text=Profile').first()

```

```yaml
- text: ApnaSamaj Connecting Communities Digitally Mobile Number
- textbox "e.g. +91 9876543210"
- text: Send OTP
- button "! ExpoSecureStore.default.getValueWithKeyA":
  - text: "! ExpoSecureStore.default.getValueWithKeyA"
  - button:
    - img
- button "Dismiss error":
  - img
- button "Minimize errors":
  - img
- button "Previous error" [disabled]:
  - img
- text: 1/1
- button "Next error" [disabled]:
  - img
- button "Reload application":
  - img
- button "Copy error":
  - img
- img
- text: Expo 57.0.0 Uncaught Error ExpoSecureStore.default.getValueWithKeyAsync is not a function
- banner:
  - text: src/store/auth.ts (47:37)
  - button "Copy content":
    - img
- text: "45 | 46 | checkAuth : async () => { > 47 | const token = await SecureStore . getItemAsync( 'access_token' ) ; | ^ 48 | const tenant = await SecureStore . getItemAsync( 'tenant_id' ) ; 49 | 50 | if (token && tenant) {"
- img
- heading "Call Stack" [level=3]
- text: "35"
- button "Show":
  - text: Show
  - img
- code: checkAuth
- code: src/store/auth.ts:47:37
- code: useEffect$argument_0
- code: app/_layout.tsx:55:5
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Mobile Tabs', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     // Navigate to root to initialize local storage
  6  |     await page.goto('/');
  7  |     
  8  |     // Inject mock auth token to bypass login on Web
  9  |     await page.evaluate(() => {
  10 |       localStorage.setItem('access_token', 'mock_token');
  11 |       localStorage.setItem('tenant_id', 'mock_tenant');
  12 |     });
  13 | 
  14 |     // Navigate to the tabs layout directly
  15 |     await page.goto('/(tabs)');
  16 |   });
  17 | 
  18 |   test('should render the Home tab', async ({ page }) => {
  19 |     // Since we mocked auth, we should be on the Home tab
  20 |     // Let's check for a text that belongs to the Home tab
  21 |     await expect(page.locator('text=Home').first()).toBeVisible();
  22 |     
  23 |     // The bottom tab bar should have all the tabs
  24 |     await expect(page.locator('text=Directory').first()).toBeVisible();
  25 |     await expect(page.locator('text=Events').first()).toBeVisible();
  26 |     await expect(page.locator('text=Donations').first()).toBeVisible();
> 27 |     await expect(page.locator('text=Profile').first()).toBeVisible();
     |                                                        ^ Error: expect(locator).toBeVisible() failed
  28 |   });
  29 | });
  30 | 
```