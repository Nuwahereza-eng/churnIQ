import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import { App } from "@/App";

/** Render the full app (layout + routes) at the given path. */
export function renderApp(path = "/") {
  const user = userEvent.setup({ applyAccept: false });
  const utils = render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
  return { user, ...utils };
}
