import AggregatedStats from "./AggregatedStatus";

import { statsFactory } from "@/mocks/factories";
import { render, screen, userEvent } from "@/utils/test-utils";

it("displays correct number of deployed machines", async () => {
  render(
    <AggregatedStats
      stats={statsFactory.build({
        total_machines: 1000,
        deployed_machines: 100,
        allocated_machines: 200,
        ready_machines: 300,
        error_machines: 400,
      })}
    />,
  );

  await userEvent.click(screen.getByRole("button", { name: /100 of 1000 deployed/i }));
  expect(screen.getByTestId("deployed")).toHaveTextContent("100");
  expect(screen.getByTestId("allocated")).toHaveTextContent("200");
  expect(screen.getByTestId("ready")).toHaveTextContent("300");
  expect(screen.getByTestId("error")).toHaveTextContent("400");
});
