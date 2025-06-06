/**
 * Jacket Allocation Logic
 * 
 * This module contains the core business logic for allocating jacket inventory to stores
 * based on current stock, previous allocations, and store capacity constraints.
 */

/**
 * Store maximum capacities (pieces)
 */
const storeCapacities = {
  "BOMBAY": 132,
  "MOGA": 257,
  "DUKE RO": 240,
  "DUKE NIT": 70,
  "MORADABAD": 158
};

/**
 * Current godown stock data (article number: quantity)
 */
const godownStock = {
  "Z2393": 27, "Z2263": 12, "Z2250": 12, "Z2327": 9, "Z2312": 7, "Z2329": 7, "Z2265": 7, 
  "Z2289": 7, "Z2308": 7, "Z2253": 7, "Z2303": 6, "Z2394": 6, "Z2333": 6, "Z2323": 6, 
  "Z2288": 5, "Z2321": 5, "Z2356": 5, "Z2272": 4, "Z2402": 4, "Z2328": 4, "Z2326": 4, 
  "Z2342": 4, "Z2377": 4, "Z2386": 4, "Z2258": 4, "Z2281": 4, "Z2294": 4, "Z2350": 4, 
  "Z2276": 4, "Z2282": 4, "Z2292": 4, "Z2330": 4, "Z2331": 3, "Z2266": 3, "Z2318": 3, 
  "Z2344": 3, "Z2254": 3, "Z2298": 3, "Z2271": 3, "Z2293": 3, "Z2279": 2, "Z2374": 2, 
  "Z2392": 2, "Z2305": 2, "Z2324": 2, "Z2362": 2, "Z2259": 2, "Z2291": 2, "Z2306": 2, 
  "Z2315": 2, "Z2341": 2, "Z2351": 2, "Z2280": 2, "Z2290": 2, "Z2297": 2, "Z2300": 2, 
  "Z2256": 2, "Z2285": 2, "Z2302": 2, "Z2268": 1, "Z2283": 1, "Z2304": 1, "Z2345": 1, 
  "Z2287": 1, "Z2301": 1, "Z2338": 1, "Z2379": 1, "Z2387": 1, "SDZ3134": 1, "Z2260": 1, 
  "Z2359": 1, "Z2391": 1, "Z2261": 1, "Z2262": 1, "Z2274": 1, "Z2335": 1, "Z2348": 1, 
  "Z2361": 1, "Z2376": 1, "Z2252": 1, "Z2278": 1, "Z2307": 1, "Z2381": 1, "SDZ2250": 1, 
  "SDZ3084R": 1, "SDZ3102": 1, "SDZ3112": 1, "SDZ3138": 1, "SDZ3170": 1, "SDZ3172": 1, 
  "Z2269": 1, "Z2286": 1, "Z2295": 1, "Z2311": 1, "Z2316": 1, "Z2319": 1, "Z2383": 1
};

/**
 * Articles sent to each store in 2024
 */
const articlesSentIn2024 = {
  "BOMBAY": ["Z2250", "Z2252", "Z2253", "Z2256", "Z2259", "Z2260", "Z2261", "Z2262", "Z2263", 
             "Z2265", "Z2266", "Z2268", "Z2271", "Z2272", "Z2276", "Z2277", "Z2278", "Z2282", 
             "Z2283", "Z2285", "Z2286", "Z2288", "Z2289", "Z2291", "Z2293", "Z2294", "Z2295", 
             "Z2297", "Z2300", "Z2301", "Z2302", "Z2304", "Z2306", "Z2307", "Z2308", "Z2311", 
             "Z2312", "Z2316", "Z2318", "Z2321", "Z2323", "Z2327", "Z2330", "Z2333", "Z2338", 
             "Z2342", "Z2344", "Z2345", "Z2348", "Z2356", "Z2361", "Z2362", "Z2374", "Z2377", 
             "Z2379", "Z2381", "Z2386", "Z2391", "Z2393", "Z2394", "Z2402"],
  
  "MOGA": ["Z2250", "Z2252", "Z2253", "Z2254", "Z2256", "Z2258", "Z2259", "Z2260", "Z2261", 
           "Z2262", "Z2263", "Z2265", "Z2266", "Z2268", "Z2269", "Z2271", "Z2272", "Z2274", 
           "Z2276", "Z2277", "Z2279", "Z2281", "Z2282", "Z2283", "Z2285", "Z2286", "Z2287", 
           "Z2288", "Z2289", "Z2290", "Z2292", "Z2293", "Z2294", "Z2295", "Z2297", "Z2298", 
           "Z2300", "Z2301", "Z2302", "Z2303", "Z2304", "Z2305", "Z2306", "Z2307", "Z2308", 
           "Z2311", "Z2312", "Z2315", "Z2316", "Z2318", "Z2319", "Z2321", "Z2323", "Z2324", 
           "Z2326", "Z2327", "Z2328", "Z2329", "Z2330", "Z2331", "Z2333", "Z2335", "Z2338", 
           "Z2341", "Z2342", "Z2344", "Z2345", "Z2348", "Z2350", "Z2351", "Z2356", "Z2359", 
           "Z2361", "Z2374", "Z2377", "Z2381", "Z2383", "Z2386", "Z2387", "Z2391", "Z2392", 
           "Z2393", "Z2394", "Z2402"],
  
  "DUKE RO": ["Z2250", "Z2252", "Z2253", "Z2256", "Z2259", "Z2260", "Z2261", "Z2262", "Z2263", 
              "Z2265", "Z2266", "Z2268", "Z2269", "Z2271", "Z2272", "Z2274", "Z2276", "Z2277", 
              "Z2278", "Z2279", "Z2280", "Z2282", "Z2283", "Z2285", "Z2286", "Z2288", "Z2289", 
              "Z2291", "Z2292", "Z2293", "Z2294", "Z2295", "Z2297", "Z2300", "Z2301", "Z2302", 
              "Z2304", "Z2306", "Z2307", "Z2308", "Z2311", "Z2312", "Z2315", "Z2316", "Z2318", 
              "Z2321", "Z2323", "Z2327", "Z2330", "Z2333", "Z2338", "Z2341", "Z2342", "Z2344", 
              "Z2345", "Z2348", "Z2356", "Z2359", "Z2361", "Z2362", "Z2374", "Z2377", "Z2379", 
              "Z2381", "Z2383", "Z2386", "Z2387", "Z2391", "Z2392", "Z2393", "Z2394", "Z2402", 
              "Z9188CM", "SDZ2250", "SDZ3084R", "SDZ3102", "SDZ3108", "SDZ3112", "SDZ3134", 
              "SDZ3138", "SDZ3161", "SDZ3170", "SDZ3172"],
  
  "DUKE NIT": ["Z2250", "Z2253", "Z2260", "Z2261", "Z2262", "Z2263", "Z2266", "Z2268", "Z2271", 
               "Z2272", "Z2276", "Z2277", "Z2278", "Z2282", "Z2283", "Z2288", "Z2289", "Z2291", 
               "Z2293", "Z2295", "Z2297", "Z2301", "Z2302", "Z2304", "Z2306", "Z2307", "Z2308", 
               "Z2311", "Z2312", "Z2315", "Z2316", "Z2321", "Z2323", "Z2327", "Z2333", "Z2338", 
               "Z2341", "Z2342", "Z2356", "Z2361", "Z2362", "Z2374", "Z2377", "Z2386", "Z2391", 
               "Z2392", "Z2393", "Z2394", "Z2402"],
  
  "MORADABAD": ["Z2250", "Z2252", "Z2253", "Z2254", "Z2256", "Z2258", "Z2259", "Z2260", "Z2261", 
                "Z2262", "Z2263", "Z2265", "Z2266", "Z2268", "Z2271", "Z2272", "Z2276", "Z2277", 
                "Z2278", "Z2281", "Z2282", "Z2283", "Z2285", "Z2286", "Z2287", "Z2288", "Z2289", 
                "Z2290", "Z2291", "Z2293", "Z2294", "Z2295", "Z2297", "Z2298", "Z2300", "Z2301", 
                "Z2302", "Z2303", "Z2304", "Z2305", "Z2306", "Z2307", "Z2308", "Z2311", "Z2312", 
                "Z2313", "Z2316", "Z2318", "Z2319", "Z2321", "Z2323", "Z2324", "Z2326", "Z2327", 
                "Z2328", "Z2329", "Z2330", "Z2331", "Z2333", "Z2335", "Z2338", "Z2342", "Z2344", 
                "Z2345", "Z2348", "Z2350", "Z2356", "Z2361", "Z2362", "Z2374", "Z2376", "Z2377", 
                "Z2379", "Z2381", "Z2386", "Z2391", "Z2393", "Z2394", "Z2402"]
};

/**
 * Calculate available articles for each store that weren't sent in 2024
 * @returns {Object} Object with store names as keys and arrays of available article numbers as values
 */
function calculateAvailableArticles() {
  const availableArticles = {};
  
  Object.keys(storeCapacities).forEach(store => {
    availableArticles[store] = Object.keys(godownStock).filter(article => 
      !articlesSentIn2024[store].includes(article) && godownStock[article] > 0
    );
  });
  
  return availableArticles;
}

/**
 * Create optimal allocation based on stock availability
 * @param {string} store - Store name
 * @returns {Object} Allocation details including articles, quantities, and statistics
 */
function createAllocation(store) {
  const availableArticles = calculateAvailableArticles();
  const available = availableArticles[store];
  const maxCapacity = storeCapacities[store];
  
  // Sort by quantity available (highest first)
  const sortedArticles = [...available].sort((a, b) => godownStock[b] - godownStock[a]);
  
  let allocation = [];
  let totalAllocated = 0;
  
  // Allocate articles respecting capacity constraints
  for (const article of sortedArticles) {
    if (totalAllocated < maxCapacity && godownStock[article] > 0) {
      // Allocate one piece of this article
      allocation.push({
        article,
        quantity: 1,
        availableInGodown: godownStock[article]
      });
      totalAllocated += 1;
      
      if (totalAllocated >= maxCapacity) break;
    }
  }
  
  return {
    allocation,
    totalAllocated,
    capacityPercentage: (totalAllocated / maxCapacity * 100).toFixed(1),
    availableArticlesCount: available.length
  };
}

/**
 * Generate comprehensive allocation report for all stores
 * @returns {Object} Allocation reports for all stores
 */
function generateAllocationReport() {
  const report = {};
  const availableArticles = calculateAvailableArticles();
  
  Object.keys(storeCapacities).forEach(store => {
    const storeAllocation = createAllocation(store);
    
    report[store] = {
      maxCapacity: storeCapacities[store],
      totalAllocated: storeAllocation.totalAllocated,
      capacityPercentage: storeAllocation.capacityPercentage,
      availableArticlesCount: availableArticles[store].length,
      allocation: storeAllocation.allocation
    };
  });
  
  return report;
}

/**
 * Generate statistics about the allocation
 * @returns {Object} Statistics about the allocation
 */
function generateAllocationStatistics() {
  const availableArticles = calculateAvailableArticles();
  
  // Calculate total available godown stock
  const totalGodownStock = Object.values(godownStock).reduce((sum, qty) => sum + qty, 0);
  
  // Calculate allocation efficiency for each store
  const storeStats = {};
  Object.keys(storeCapacities).forEach(store => {
    const allocation = createAllocation(store);
    storeStats[store] = {
      capacityUtilization: parseFloat(allocation.capacityPercentage),
      uniqueArticles: allocation.allocation.length,
      totalArticles: allocation.totalAllocated
    };
  });
  
  return {
    totalUniqueArticlesInGodown: Object.keys(godownStock).length,
    totalStockInGodown: totalGodownStock,
    storeStatistics: storeStats
  };
}

// Export the functions
module.exports = {
  calculateAvailableArticles,
  createAllocation,
  generateAllocationReport,
  generateAllocationStatistics,
  storeCapacities,
  godownStock,
  articlesSentIn2024
};
