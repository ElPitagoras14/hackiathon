import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-background border-t border-border">
      <div className="mx-auto max-w-7xl overflow-hidden px-6 py-20 sm:py-24 lg:px-8">
        <nav
          className="flex flex-wrap justify-center gap-x-2 gap-y-2"
          aria-label="Footer"
        >
          {["About", "Work", "Services", "Contact", "Privacy", "Terms"].map(
            (item) => (
              <div key={item} className="pb-6 px-4">
                <Link
                  href={`/${item.toLowerCase()}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm leading-6 text-muted-foreground hover:text-foreground"
                >
                  {item}
                </Link>
              </div>
            )
          )}
        </nav>
      </div>
    </footer>
  );
}
