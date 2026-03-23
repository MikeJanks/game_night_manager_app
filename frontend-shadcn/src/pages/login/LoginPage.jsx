import { Link } from "react-router-dom"
import AmbientBlobBackground from "@/components/AmbientBlobBackground"
import AppPageHeader from "@/components/AppPageHeader"
import { Button } from "@/components/ui/button"
import AuthLoginForm from "@/components/ui/auth-login-form"

function LoginPage() {
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

        <main className="flex min-h-0 flex-1 flex-col justify-center items-center">
          <AuthLoginForm
            onSubmit={async (data) => {
              /* demo login */
            }}
            showRememberMe={true}
          />
        </main>
      </div>
    </div>
  )
}

export default LoginPage
