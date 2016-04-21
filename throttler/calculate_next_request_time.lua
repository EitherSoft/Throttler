local request_timeout = tonumber(ARGV[1])
local last_request_time =  tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local next_request_time = now

for i, key in ipairs(KEYS) do
    local current = redis.call('GET', key)

    if (current==nil or (type(current) == "boolean" and not current)) then
        next_request_time = now + request_timeout - last_request_time
    else
        next_request_time = tonumber(current) + request_timeout - last_request_time
        if (next_request_time < now) then
            next_request_time = now
        end
    end

    redis.call('SET', key, next_request_time)

    return tostring(next_request_time)
end
