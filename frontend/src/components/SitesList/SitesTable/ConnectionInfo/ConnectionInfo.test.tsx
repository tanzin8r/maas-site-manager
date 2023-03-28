import ConnectionInfo, { connectionIcons, connectionLabels } from "./ConnectionInfo";

import { connections } from "@/mocks/factories";
import { render, screen } from "@/test-utils";

connections.forEach((connection) => {
  it(`displays correct connection status icon and label for ${connection} connection`, () => {
    const { container } = render(<ConnectionInfo connection={connection} />);
    expect(screen.getByText(connectionLabels[connection])).toBeInTheDocument();
    // eslint-disable-next-line testing-library/no-container
    expect(container.querySelector(".status-icon")).toHaveClass(connectionIcons[connection]);
  });
});
