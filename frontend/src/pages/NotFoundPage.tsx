import { Link } from "react-router-dom";

import { EmptyState } from "@/components/States";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function NotFoundPage() {
  return (
    <Card className="mx-auto mt-10 max-w-lg">
      <EmptyState
        title="Page not found"
        description="The page you are looking for does not exist."
        action={
          <Button asChild variant="outline">
            <Link to="/">Back to overview</Link>
          </Button>
        }
      />
    </Card>
  );
}
