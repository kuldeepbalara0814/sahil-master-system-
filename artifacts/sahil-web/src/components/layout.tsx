import { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import { Home, Zap, FileEdit, List, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface LayoutProps {
  children: ReactNode;
  title: string;
}

export function Layout({ children, title }: LayoutProps) {
  const [location] = useLocation();

  const navItems = [
    { href: "/", icon: Home, label: "Home" },
    { href: "/predict", icon: Zap, label: "Predict" },
    { href: "/result", icon: FileEdit, label: "Result" },
    { href: "/records", icon: List, label: "Records" },
    { href: "/tracker", icon: Activity, label: "Tracker" },
  ];

  return (
    <div className="flex flex-col min-h-[100dvh] bg-background text-foreground pb-16">
      <header className="sticky top-0 z-10 bg-card border-b border-border px-4 py-4 flex items-center justify-between shadow-sm">
        <h1 className="text-xl font-bold tracking-tight text-primary">{title}</h1>
      </header>

      <main className="flex-1 p-4 overflow-x-hidden">
        {children}
      </main>

      <nav className="fixed bottom-0 left-0 right-0 z-20 bg-card border-t border-border pb-safe">
        <ul className="flex items-center justify-around">
          {navItems.map((item) => {
            const isActive = location === item.href;
            const Icon = item.icon;
            return (
              <li key={item.href} className="flex-1">
                <Link
                  href={item.href}
                  className={cn(
                    "flex flex-col items-center justify-center w-full py-3 gap-1 text-xs transition-colors",
                    isActive ? "text-primary font-semibold" : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <Icon className={cn("w-5 h-5", isActive ? "fill-primary/20" : "")} />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
