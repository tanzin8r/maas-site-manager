// src/mocks/browser.js
import { setupWorker, rest } from "msw";

const getMockSite = () => ({
  name: "maas-example-region",
  url: "maas.example.com",
  connection: "stable",
  address: {
    countrycode: "DE", // <alpha2 country code>,
    city: "Berlin",
    zip: "10405",
    street: "Prenzlauer Allee 132",
  },
  timezone: "CET", // <three letter abbreviation>,
  stats: {
    machines: 300,
    occupied_machines: 289,
    ready_machines: 11,
    error_machines: 0,
  },
});

const worker = setupWorker(
  rest.get(
    "/sites",
    // Example of a response resolver that returns
    // a "Content-Type: application/json" response.
    (req, res, ctx) => {
      return res(
        ctx.json({
          items: [getMockSite()],
          total: 42,
          page: 1,
          size: 20,
        })
      );
    }
  )
);

worker.start();
