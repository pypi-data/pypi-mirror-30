#pragma once

#include <unistd.h>
#include <linux/perf_event.h>

#include <cstdint>
#include <cstring>
#include <iostream>
#include <vector>
#include <string>

namespace libperf {

    extern const char* version_;
    
    class FDGuard {
    public:
        
        long int fd;
        bool set;

        FDGuard(void) :
            fd(-1),
            set(false)
        { }
        
        FDGuard(long int fd_) :
            fd(fd_),
            set(true)
        { }

        ~FDGuard(){
            if(set){
                close(fd);
            }
        }
    };
        
    typedef struct perf_event_attr perf_event_attr_;
    
    struct libperf_counter_ {

        std::string name;
        perf_event_attr attributes;


        libperf_counter_(std::string _name){
            name = _name;
            
            attributes = {};

            std::memset(&attributes, 0, sizeof(perf_event_attr));            
        }
        
        libperf_counter_(const char *_name,
                        decltype(perf_event_attr_().type) _type,
                        decltype(perf_event_attr_().config) _config) {

            name = std::string(_name);

            attributes = {};
            std::memset(&attributes, 0, sizeof(perf_event_attr));

            attributes.type = _type;
            attributes.config = _config;
        }
    };

    typedef struct libperf_counter_ libperf_counter_;

    const libperf_counter_ counters_[] = {
        libperf_counter_("LIBPERF_COUNT_SW_CPU_CLOCK", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_CPU_CLOCK),
        libperf_counter_("LIBPERF_COUNT_SW_TASK_CLOCK", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_TASK_CLOCK),
        libperf_counter_("LIBPERF_COUNT_SW_CONTEXT_SWITCHES", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_CONTEXT_SWITCHES),
        libperf_counter_("LIBPERF_COUNT_SW_CPU_MIGRATIONS", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_CPU_MIGRATIONS),
        libperf_counter_("LIBPERF_COUNT_SW_PAGE_FAULTS", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_PAGE_FAULTS),
        libperf_counter_("LIBPERF_COUNT_SW_PAGE_FAULTS_MIN", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_PAGE_FAULTS_MIN),
        libperf_counter_("LIBPERF_COUNT_SW_PAGE_FAULTS_MAJ", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_PAGE_FAULTS_MAJ),
        
        libperf_counter_("LIBPERF_COUNT_HW_CPU_CYCLES", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES),
        libperf_counter_("LIBPERF_COUNT_HW_INSTRUCTIONS", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_REFERENCES", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CACHE_REFERENCES),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_MISSES", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CACHE_MISSES),
        libperf_counter_("LIBPERF_COUNT_HW_BRANCH_INSTRUCTIONS", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS),
        libperf_counter_("LIBPERF_COUNT_HW_BRANCH_MISSES", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_MISSES),
        libperf_counter_("LIBPERF_COUNT_HW_BUS_CYCLES", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BUS_CYCLES),
        
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_L1D_LOADS", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_L1D_LOADS_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_L1D_STORES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_L1D_STORES_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_L1D_PREFETCHES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_PREFETCH << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_L1I_LOADS", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_L1I | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_L1I_LOADS_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_L1I | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_LL_LOADS", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_LL | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_LL_LOADS_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_LL | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_LL_STORES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_LL | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_LL_STORES_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_LL | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_DTLB_LOADS", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_DTLB_LOADS_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_DTLB_STORES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_DTLB_STORES_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_ITLB_LOADS", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_ITLB | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_ITLB_LOADS_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_ITLB | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_BPU_LOADS", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_BPU | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16))),
        libperf_counter_("LIBPERF_COUNT_HW_CACHE_BPU_LOADS_MISSES", PERF_TYPE_HW_CACHE, (PERF_COUNT_HW_CACHE_BPU | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16))),
    };
    
    const size_t num_available_counters_ = sizeof(counters_) / sizeof(libperf_counter_);

    int open_counter(libperf_counter_ &counter);
    libperf_counter_ get_counter_by_name(std::string counter_name);
    bool is_counter_available(std::string counter_name);
    std::vector<std::string> get_counters_available(void);
    
    class PerfCounter {
    public:

        PerfCounter(std::string counter_name);
        PerfCounter() = delete;
        ~PerfCounter(void);
        
        void start(void);
        void stop(void);
        void reset(void);
        uint64_t getval(void);
        
    private:

        libperf_counter_ counter_;
        const std::string &name_;
        int fd_;
        
    };
    
}
