import type { Stats } from "@/api/types";
import Meter, { color } from "@/components/Meter";
import Popover from "@/components/Popover/Popover";

const AggregatedStatus = ({ stats }: { stats: Stats }) => {
  const { deployed_machines, allocated_machines, ready_machines, error_machines, total_machines } = stats;
  return (
    <>
      <div>
        <Popover
          content={
            <>
              <div className="p-popover__primary">
                <div className="u-vertically-center">
                  <i className="p-icon--status-deployed"></i>
                </div>
                <div className="u-align--right" data-testid="deployed">
                  {deployed_machines}
                </div>
                <div>Deployed</div>
                <div className="u-vertically-center">
                  <i className="p-icon--status-allocated"></i>
                </div>
                <div className="u-align--right" data-testid="allocated">
                  {allocated_machines}
                </div>
                <div>Allocated</div>
                <div className="u-vertically-center">
                  <i className="p-icon--status-ready"></i>
                </div>
                <div className="u-align--right" data-testid="ready">
                  {ready_machines}
                </div>
                <div>Ready / New</div>
              </div>
              <div className="p-popover__secondary">
                <div />
                <div className="u-align--right" data-testid="error">
                  {error_machines}
                </div>
                <div>Error</div>
              </div>
            </>
          }
        >
          <Meter
            className="u-no-margin--bottom u-no-padding"
            data={[
              { color: "black", value: deployed_machines },
              { color: color.link, value: allocated_machines },
              { color: color.linkFaded, value: ready_machines },
            ]}
            label={`${deployed_machines} of ${total_machines} deployed`}
            labelClassName="u-text--muted"
            small
          />
        </Popover>
      </div>
    </>
  );
};

export default AggregatedStatus;
