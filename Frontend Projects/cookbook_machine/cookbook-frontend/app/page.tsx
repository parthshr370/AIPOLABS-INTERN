import { CookbookGenerator } from "@/components/cookbook-generator"
import { Cog } from "lucide-react"
import { Button } from "@/components/ui/button"
import Image from "next/image"

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-grow">
        <CookbookGenerator />
      </main>
    </div>
  )
}
