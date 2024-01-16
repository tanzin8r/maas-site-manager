import { ContentSection, MainToolbar } from "@canonical/maas-react-components";
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
  const { page, debouncedPage, size, handlePageSizeChange, setPage } = usePagination(DEFAULT_PAGE_SIZE);
  const [searchText, setSearchText] = useState("");
  const debounceSearchText = useDebounce(searchText);
  const { setSidebar } = useAppLayoutContext();
  const [sorting, setSorting] = useState<SortingState>([]);
  const sortBy = getSortBy(sorting) as SortBy<UserSortKey>;

  const { data, error, isPending } = useUsersQuery({
    page: debouncedPage,
    size,
    sortBy,
    searchText: parseSearchTextToUrlFreeTextSearch(debounceSearchText),
  });

  useEffect(() => {
    setPage(1);
  }, [searchText, setPage]);

  const handleSearchInput = (inputValue: string) => {
    setSearchText(inputValue);
  };

  return (
    <ContentSection className="user-list">
      <ContentSection.Header>
        <MainToolbar>
          <MainToolbar.Title>Users</MainToolbar.Title>
          <MainToolbar.Controls>
            <SearchBox
              className="user-list__search"
              externallyControlled
              onChange={handleSearchInput}
              placeholder="Search"
            />
            <button onClick={() => setSidebar("addUser")} type="button">
              Add user
            </button>
          </MainToolbar.Controls>
        </MainToolbar>
        <PaginationBar
          currentPage={page}
          dataContext="users"
          handlePageSizeChange={handlePageSizeChange}
          isPending={isPending}
          itemsPerPage={size}
          setCurrentPage={setPage}
          totalItems={data?.total || 0}
        />
      </ContentSection.Header>
      <ContentSection.Content>
        <UserListTable data={data} error={error} isPending={isPending} setSorting={setSorting} sorting={sorting} />
      </ContentSection.Content>
    </ContentSection>
  );
};

export default UserList;
