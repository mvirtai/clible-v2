import { ChevronRight } from 'lucide-react';
import type { SearchResponse } from '../types/search';
import { SearchStatsPanel } from './SearchStatsPanel';

interface SearchViewProps {
  searchResponse: SearchResponse | null;
  onResultClick: (reference: string) => void;
}

export function SearchView({ searchResponse, onResultClick }: SearchViewProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 border-b border-[#F5F5F5] pb-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-serif italic">Search Results</h2>
          {searchResponse && (
            <span className="text-sm text-[#8E8E8E]">
              {searchResponse.statistics.uniqueVerses} unique verse
              {searchResponse.statistics.uniqueVerses === 1 ? '' : 's'}
            </span>
          )}
        </div>
        {searchResponse && (
          <SearchStatsPanel
            statistics={searchResponse.statistics}
            rowCount={searchResponse.rows.length}
          />
        )}
      </div>
      {searchResponse && searchResponse.rows.length === 0 && (
        <p className="text-center text-[#8E8E8E] py-8">No verses found for this search.</p>
      )}
      <div className="space-y-4">
        {searchResponse?.rows.map((res, i) => (
          <button
            key={i}
            onClick={() => onResultClick(res.reference)}
            className="w-full text-left p-6 bg-white border border-[#E5E5E5] rounded-2xl hover:border-[#1A1A1A] transition-all group"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="font-bold text-[#D4A373]">{res.reference}</span>
              <ChevronRight size={16} className="text-[#E5E5E5] group-hover:text-[#1A1A1A] transition-colors" />
            </div>
            <p className="text-[#4A4A4A] line-clamp-2">{res.text}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
