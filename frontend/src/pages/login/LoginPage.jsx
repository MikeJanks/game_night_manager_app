import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import AmbientBlobBackground from "@/components/AmbientBlobBackground"
import AppPageHeader from "@/components/AppPageHeader"
import { Button } from "@/components/ui/button"
import AuthLoginForm from "@/components/ui/auth-login-form"
import { useAuth } from "@/contexts/AuthContext"


function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [errors, setErrors] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  
  return (
    <div className="relative flex h-dvh w-full flex-col overflow-hidden bg-background text-foreground">
      <AmbientBlobBackground />

      <div className="relative z-10 flex min-h-0 flex-1 flex-col">
        <AppPageHeader title="Log in" icon="login">
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
          <AuthLoginForm
            onSubmit={async (data) => {
              setErrors({})
              setIsLoading(true)
              try {
                await login(data.email, data.password)
                navigate("/chat", { replace: true })
              } catch (e) {
                setErrors({ general: e instanceof Error ? e.message : "Something went wrong" })
              } finally {
                setIsLoading(false)
              }
            }}
            errors={errors}
            isLoading={isLoading}
            showRememberMe={false}
            showSocialLogin={false}
            footer={
              <p>
                Don&apos;t have an account?{" "}
                <Link
                  to="/signup"
                  className="text-primary font-medium underline-offset-4 hover:underline"
                >
                  Sign up
                </Link>
              </p>
            }
          />
        </main>
      </div>
    </div>
  )
}

export default LoginPage
