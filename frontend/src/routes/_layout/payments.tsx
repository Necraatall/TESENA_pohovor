import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  type PaymentPublic,
  type PaymentScenario,
  PaymentsService,
} from "@/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  orderId: z.string().min(1, { message: "Order ID is required" }),
  amount: z
    .string()
    .regex(/^\d{1,10}(\.\d{1,2})?$/, {
      message: "Enter a positive amount with at most 2 decimal places",
    })
    .refine((value) => Number(value) > 0, {
      message: "Amount must be greater than 0",
    }),
  scenario: z.enum(["success", "declined", "timeout"]),
})

type FormData = z.infer<typeof formSchema>

const resultMessages = {
  PAID: "Payment successful.",
  FAILED: "Payment declined. Please try another payment method.",
  PENDING:
    "Payment is still being processed. The final result is not available yet.",
} as const

export const Route = createFileRoute("/_layout/payments")({
  component: PaymentDemo,
  head: () => ({
    meta: [
      {
        title: "Payment Demo - FastAPI Template",
      },
    ],
  }),
})

function PaymentDemo() {
  const [payment, setPayment] = useState<PaymentPublic | null>(null)
  const { showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      orderId: "ORD-123",
      amount: "1250",
      scenario: "success",
    },
  })

  const currentOrderId = form.watch("orderId")
  const retryBlocked =
    payment?.order_id === currentOrderId &&
    (payment.status === "PAID" || payment.status === "PENDING")

  const mutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await PaymentsService.createOrderPayment({
        path: { order_id: data.orderId },
        body: {
          amount: data.amount,
          scenario: data.scenario as PaymentScenario,
        },
      })
      return response.data
    },
    onSuccess: (data) => {
      setPayment(data)
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data)
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Payment Demo</h1>
        <p className="text-muted-foreground">
          Run deterministic payment scenarios against the FastAPI backend.
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Create payment</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              className="flex flex-col gap-5"
              onSubmit={form.handleSubmit(onSubmit)}
            >
              <FormField
                control={form.control}
                name="orderId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Order ID</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="ORD-123" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Amount (CZK)</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        inputMode="decimal"
                        placeholder="1250"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="scenario"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Scenario</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select scenario" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="success">
                          Successful payment
                        </SelectItem>
                        <SelectItem value="declined">
                          Declined payment
                        </SelectItem>
                        <SelectItem value="timeout">Timeout</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <LoadingButton
                type="submit"
                loading={mutation.isPending}
                disabled={retryBlocked}
                className="w-fit"
              >
                Pay
              </LoadingButton>

              {retryBlocked && (
                <p className="text-sm text-muted-foreground">
                  This order already has a {payment?.status.toLowerCase()}{" "}
                  payment. Use a new Order ID to run another payment attempt.
                </p>
              )}
            </form>
          </Form>
        </CardContent>
      </Card>

      {payment && (
        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle>{payment.status}</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <p>{resultMessages[payment.status]}</p>

            {payment.status === "FAILED" && (
              <p className="text-sm text-muted-foreground">
                You can retry this Order ID with another payment attempt.
              </p>
            )}

            <dl className="grid gap-2 text-sm">
              <div>
                <dt className="font-medium">Order ID</dt>
                <dd className="font-mono break-all">{payment.order_id}</dd>
              </div>
              <div>
                <dt className="font-medium">Amount</dt>
                <dd>
                  {payment.amount} {payment.currency}
                </dd>
              </div>
              <div>
                <dt className="font-medium">Payment ID</dt>
                <dd className="font-mono break-all">{payment.payment_id}</dd>
              </div>
              <div>
                <dt className="font-medium">Transaction ID</dt>
                <dd className="font-mono break-all">
                  {payment.transaction_id}
                </dd>
              </div>
              <div>
                <dt className="font-medium">Correlation ID</dt>
                <dd className="font-mono break-all">
                  {payment.created_by_correlation_id}
                </dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
