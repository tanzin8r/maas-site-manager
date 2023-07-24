import ExternalLink from "@/components/ExternalLink";
import TableCaption from "@/components/TableCaption";
import docsUrls from "@/config/docsUrls";
import { useRequestsCountQuery } from "@/hooks/react-query";
import { Link } from "@/utils/router";

const NoRegions = () => {
  const { data, isSuccess } = useRequestsCountQuery();

  return (
    <TableCaption>
      <TableCaption.Title>No enroled MAAS regions</TableCaption.Title>
      {isSuccess && data.total > 0 ? (
        <>
          <TableCaption.Description>
            You have <strong>{data?.total} open enrolment requests, </strong>inspect them in the Requests page.
            <br />
            <ExternalLink to={docsUrls.enrollmentRequest}>
              Learn more about the enrolment process in the documentation.
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
            To enrol follow the steps in the Tokens page.
            <br />
            <ExternalLink to={docsUrls.enrollmentRequest}>
              Learn more about the enrolment process in the documentation.
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

export default NoRegions;
