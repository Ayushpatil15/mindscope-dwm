import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface GlobalFilters {
  country: string;
  platform: string;
  academic_level: string;
  gender: string;
  stress_level: string;
}

const defaultFilters: GlobalFilters = {
  country: 'All',
  platform: 'All',
  academic_level: 'All',
  gender: 'All',
  stress_level: 'All',
};

interface FilterContextType {
  filters: GlobalFilters;
  setFilter: (key: keyof GlobalFilters, value: string) => void;
  resetFilters: () => void;
  toQueryString: () => string;
}

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [filters, setFilters] = useState<GlobalFilters>(defaultFilters);

  const setFilter = (key: keyof GlobalFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
  };

  const toQueryString = () => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v && v !== 'All') {
        params.append(k, v);
      }
    });
    const qs = params.toString();
    return qs ? `?${qs}` : '';
  };

  return (
    <FilterContext.Provider value={{ filters, setFilter, resetFilters, toQueryString }}>
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};

