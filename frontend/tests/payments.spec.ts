import { expect, test } from "@playwright/test"

function uniqueOrderId(scenario: string): string {
  return `PW-${scenario}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

test("Successful payment is shown as PAID", async ({ page }) => {
  const orderId = uniqueOrderId("SUCCESS")

  await page.goto("/payments")

  await expect(
    page.getByRole("heading", { name: "Payment Demo" }),
  ).toBeVisible()

  await page.getByLabel("Order ID").fill(orderId)
  await page.getByLabel("Amount (CZK)").fill("1250.50")
  await page.getByRole("button", { name: "Pay" }).click()

  await expect(page.getByText("PAID", { exact: true })).toBeVisible()
  await expect(page.getByText("Payment successful.")).toBeVisible()
  await expect(page.getByText(orderId, { exact: true })).toBeVisible()
})

test("Declined payment is shown as FAILED", async ({ page }) => {
  const orderId = uniqueOrderId("DECLINED")

  await page.goto("/payments")

  await page.getByLabel("Order ID").fill(orderId)
  await page.getByLabel("Amount (CZK)").fill("1250.50")

  await page.getByRole("combobox").click()
  await page.getByRole("option", { name: "Declined payment" }).click()

  await page.getByRole("button", { name: "Pay" }).click()

  await expect(page.getByText("FAILED", { exact: true })).toBeVisible()
  await expect(
    page.getByText("Payment declined. Please try another payment method."),
  ).toBeVisible()
  await expect(page.getByText(orderId, { exact: true })).toBeVisible()
})
