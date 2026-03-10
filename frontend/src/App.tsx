// frontend/src/App.tsx:
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Index from "./pages/Index";
import CreateGame from "./pages/CreateGame";
import GameWorkspace from "./pages/GameWorkspace";
import NotFound from "./pages/NotFound";
import RequireAuth from "./components/RequireAuth";
import Auth from "./pages/Auth";
import VerifyEmail from "./pages/VerifyEmail";
import ProtectedRoute from "./components/ProtectedRoute";

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/",
    element: <Index />,
  },
  {
    path: "/auth",
    element: <Auth />,
  },
  {
    path: "/create-game",
    element: (
      <RequireAuth>
        <CreateGame />
      </RequireAuth>
    ),
  },
  {
    path: "/game-workspace",
    element: (
      <RequireAuth>
        <GameWorkspace />
      </RequireAuth>
    ),
  },
  {
    path: "*",
    element: <NotFound />,
  },
   { path: "/verify-email", element: <VerifyEmail /> },
]);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <RouterProvider router={router} />
      <Toaster />
      <Sonner />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
