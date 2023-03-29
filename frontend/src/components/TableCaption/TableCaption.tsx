const TableCaption = ({ children }: { children: React.ReactNode }) => (
  <caption>
    <div className="p-strip">{children}</div>
  </caption>
);

const Title = ({ children }: { children: React.ReactNode }) => (
  <div className="row">
    <div className="col-start-large-4 u-align--left col-8 col-medium-4 col-small-3">
      <p className="p-heading--4 u-no-margin--bottom">{children}</p>
    </div>
  </div>
);

const Description = ({ children }: { children: React.ReactNode }) => (
  <div className="row">
    <div className="u-align--left col-start-large-4 col-8 col-medium-4 col-small-3">
      <p>{children}</p>
    </div>
  </div>
);

TableCaption.Title = Title;
TableCaption.Description = Description;

export default TableCaption;
