#include "libperf.hh"

#include <fcntl.h>
#include <stropts.h>
#include <unistd.h>
#include <sys/syscall.h>

#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

const char* libperf::version_ = "0.4";

int libperf::open_counter(libperf_counter_ &counter) {

    pid_t pid = syscall(SYS_gettid);
    int cpu = -1;
    
    int fd = syscall(__NR_perf_event_open,
                 &counter.attributes, pid, cpu,
                 -1, 0);
    
    return fd;
    
}

libperf::libperf_counter_ libperf::get_counter_by_name(std::string counter_name) {

    libperf::libperf_counter_ counter{counter_name};
    
    bool counter_exists = false;
    for(size_t i = 0; i < libperf::num_available_counters_; i++) {
        if( counter_name.compare(counters_[i].name) == 0 ){
            counter = libperf::counters_[i];
            counter_exists = true;
            break;
        }
    }
    
    if(not counter_exists){
        throw std::runtime_error("'" + counter_name + "' does not name a defined perf counter.");
    }

    return counter;
}

bool libperf::is_counter_available(std::string counter_name) {

    libperf::libperf_counter_ counter = libperf::get_counter_by_name(counter_name);
    
    counter.attributes.size = sizeof(perf_event_attr);
    counter.attributes.inherit = 1;
    counter.attributes.disabled = 1;
    counter.attributes.enable_on_exec = 0;
    
    libperf::FDGuard fdg{libperf::open_counter(counter)};
    
    if(fdg.fd < 0){
        return false;
    }
    return true;
}


std::vector<std::string> libperf::get_counters_available(void) {

    std::vector<std::string> counters{};
    for(size_t i = 0; i < libperf::num_available_counters_; i++){
        
        std::string name = libperf::counters_[i].name;
        if(libperf::is_counter_available(name)) {
            counters.push_back(name);
        }
    }

    return counters;
}

libperf::PerfCounter::PerfCounter(std::string counter_name) :
    counter_(counter_name),
    name_(counter_.name)
{
    
    if(not libperf::is_counter_available(counter_name) ){
        throw std::runtime_error("'" + counter_name + "' is not available on your system!");
    }
    
    counter_ = libperf::get_counter_by_name(counter_name);
    
    counter_.attributes.size = sizeof(perf_event_attr);
    counter_.attributes.inherit = 1;
    counter_.attributes.disabled = 1;
    counter_.attributes.enable_on_exec = 0;

    fd_ = libperf::open_counter(counter_);

    // run once to warm things up
    this->start();
    this->stop();    
    this->reset();
}

libperf::PerfCounter::~PerfCounter(void) {
    close(fd_);
}

void libperf::PerfCounter::start(void) {
    
    int ret = ioctl(fd_, PERF_EVENT_IOC_ENABLE);
    if(ret < 0){
        throw std::runtime_error("Failed to start " + name_ + " counter.");
    }        
}

void libperf::PerfCounter::stop(void) {

    int ret =  ioctl(fd_, PERF_EVENT_IOC_DISABLE);
    if(ret < 0){
        throw std::runtime_error("Failed to stop " + counter_.name + " counter.");
    }        
    
}

void libperf::PerfCounter::reset(void) {

    close(fd_);

    std::memset(&counter_.attributes, 0, sizeof(perf_event_attr));
    counter_.attributes.size = sizeof(perf_event_attr);
    counter_.attributes.inherit = 1;
    counter_.attributes.disabled = 1;
    counter_.attributes.enable_on_exec = 0;

    fd_ = libperf::open_counter(counter_);
    
}

uint64_t libperf::PerfCounter::getval(void) {

    uint64_t value;
    
    int bytes_read = read(fd_, &value, sizeof(uint64_t));
    if(bytes_read != sizeof(uint64_t)){
        throw std::runtime_error("Failed to read the value of " + counter_.name + " counter. (retval of `read` call was " + std::to_string(bytes_read) + ")");
    }            
    
    return value;
}
