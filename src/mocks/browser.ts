// src/mocks/browser.js
import { setupWorker, rest } from "msw";

const getMockSite = (site = {}) => ({
  name: "maas-example-region",
  url: "http://maas.example.com",
  connection: "stable",
  last_seen: "2020-10-20T12:00:00Z",
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
  ...site,
});

const worker = setupWorker(
  rest.get("/sites", (req, res, ctx) => {
    return res(
      ctx.json({
        items: [
          getMockSite(),
          getMockSite({
            name: "maas-shanghai",
            url: "http://maas.shanghai.com",
            address: {
              countrycode: "CHN",
              city: "Shanghai",
              zip: "200000",
              street: "Xinzhen Road 3",
            },
            timezone: "CST",
          }),
        ],
        total: 42,
        page: 1,
        size: 20,
      })
    );
  })
);

worker.start();
