import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import AmbientBlobBackground from "@/components/AmbientBlobBackground"
import AppPageHeader from "@/components/AppPageHeader"
import { Button } from "@/components/ui/button"
import AuthSignupForm from "@/components/ui/auth-signup-form"
import login from "@/apis/login"
import signup from "@/apis/signup"

function SignupPage() {
  const navigate = useNavigate()
  const [errors, setErrors] = useState({})
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="relative flex h-dvh w-full flex-col overflow-hidden bg-background text-foreground">
      <AmbientBlobBackground />

      <div className="relative z-10 flex min-h-0 flex-1 flex-col">
        <AppPageHeader title="Sign up" icon="person_add">
          <Button
            variant="outline"
            size="sm"
            className="px-4 py-2 text-sm font-medium border-border bg-card hover:bg-muted"
            asChild
          >
            <Link to="/">Home</Link>
          </Button>
        </AppPageHeader>

        <main className="flex h-full flex-1 flex-col items-center-safe justify-center-safe overflow-y-auto px-6 p-8">
          <AuthSignupForm
            onSubmit={async (data) => {
              setErrors({})
              setIsLoading(true)
              try {
                await signup({
                  username: data.username,
                  email: data.email,
                  password: data.password,
                })
                const { access_token } = await login({
                  username: data.email,
                  password: data.password,
                })
                localStorage.setItem("access_token", access_token)
                navigate("/chat", { replace: true })
              } catch (e) {
                setErrors({
                  general: e instanceof Error ? e.message : "Something went wrong",
                })
              } finally {
                setIsLoading(false)
              }
            }}
            errors={errors}
            isLoading={isLoading}
            showSocialLogin={false}
            footer={
              <p>
                Already have an account?{" "}
                <Link
                  to="/login"
                  className="text-primary font-medium underline-offset-4 hover:underline"
                >
                  Log in
                </Link>
              </p>
            }
          />
        </main>
      </div>
    </div>
  )
}

export default SignupPage
