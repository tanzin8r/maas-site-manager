import { SearchBox } from "@canonical/react-components";
import type { SortingState } from "@tanstack/react-table";

import UserListTable from "./UserListTable";

import type { SortBy, UserSortKey } from "@/api/handlers";
import PaginationBar from "@/components/base/PaginationBar/PaginationBar";
import { useAppLayoutContext } from "@/context";
import { useUsersQuery } from "@/hooks/react-query";
import useDebounce from "@/hooks/useDebouncedValue";
import usePagination from "@/hooks/usePagination";
import { getSortBy, parseSearchTextToUrlFreeTextSearch } from "@/utils";

const DEFAULT_PAGE_SIZE = 50;

const UserList = () => {
  const [totalDataCount, setTotalDataCount] = useState(0);
  const { page, debouncedPage, size, handleNextClick, handlePreviousClick, handlePageSizeChange, setPage } =
    usePagination(DEFAULT_PAGE_SIZE, totalDataCount);
  const [searchText, setSearchText] = useState("");
  const debounceSearchText = useDebounce(searchText);
  const { setSidebar } = useAppLayoutContext();
  const [sorting, setSorting] = useState<SortingState>([]);
  const sortBy = getSortBy(sorting) as SortBy<UserSortKey>;

  const { data, error, isLoading } = useUsersQuery(
    {
      page: `${debouncedPage}`,
      size: `${size}`,
      sort_by: sortBy,
    },
    parseSearchTextToUrlFreeTextSearch(debounceSearchText),
  );

  useEffect(() => {
    setPage(1);
  }, [searchText, setPage]);

  useEffect(() => {
    if (data && "total" in data) {
      setTotalDataCount(data.total);
    }
  }, [data]);

  const handleSearchInput = (inputValue: string) => {
    setSearchText(inputValue);
  };

  return (
    <section className="user-list">
      <header className="user-list__header">
        <div className="u-flex--grow">
          <SearchBox
            className="user-list__search"
            externallyControlled
            onChange={handleSearchInput}
            placeholder="Search"
          />
        </div>
        <div className="u-flex u-flex--justify-end">
          <button onClick={() => setSidebar("addUser")} type="button">
            Add user
          </button>
        </div>
      </header>
      <PaginationBar
        currentPage={page}
        dataContext="users"
        handlePageSizeChange={handlePageSizeChange}
        isLoading={isLoading}
        itemsPerPage={size}
        onNextClick={handleNextClick}
        onPreviousClick={handlePreviousClick}
        setCurrentPage={setPage}
        totalItems={data?.total || 0}
      />
      <UserListTable data={data} error={error} isLoading={isLoading} setSorting={setSorting} sorting={sorting} />
    </section>
  );
};

export default UserList;
