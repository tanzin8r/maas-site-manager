import { ExternalLink } from "@canonical/maas-react-components";

import { useEnrollmentRequests } from "@/api/query/enrollmentRequests";
import TableCaption from "@/components/TableCaption";
import docsUrls from "@/config/docsUrls";
import { Link } from "@/utils/router";

const NoSites = () => {
  const { data, isSuccess } = useEnrollmentRequests({ query: { page: 1, size: 0 } });

  return (
    <TableCaption>
      <TableCaption.Title>No enrolled MAAS sites</TableCaption.Title>
      {isSuccess && data.total > 0 ? (
        <>
          <TableCaption.Description>
            You have <strong>{data?.total} open enrollment requests, </strong>inspect them in the Requests page.
            <br />
            <ExternalLink to={docsUrls.enrollmentRequest}>
              Learn more about the enrollment process in the documentation.
            </ExternalLink>
          </TableCaption.Description>
          <TableCaption.Description>
            <Link className="p-button--positive" to="/settings/requests">
              Go to Requests Page
            </Link>
          </TableCaption.Description>
        </>
      ) : (
        <>
          <TableCaption.Description>
            To enroll follow the steps in the Tokens page.
            <br />
            <ExternalLink to={docsUrls.enrollmentRequest}>
              Learn more about the enrollment process in the documentation.
            </ExternalLink>
          </TableCaption.Description>
          <TableCaption.Description>
            <Link className="p-button--positive" to="/settings/tokens">
              Go to Tokens page
            </Link>
          </TableCaption.Description>
        </>
      )}
    </TableCaption>
  );
};

export default NoSites;
