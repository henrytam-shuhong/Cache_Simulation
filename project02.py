



instruction_set = []
main_memory = []
cache = []

# Store a block of data in the cache
class Cache_row:
    def __init__(self, slot=0, valid = 0, tag = 0, dirty = 0, data = [0] * 16):
        self.slot = slot
        self.valid = valid
        self.tag = tag
        self.dirty = dirty
        self.data = data

# Initiate cache
for i in range(16):
    cache.append(Cache_row(i))

# Initiate Main_memory
for i in range (2048):
    main_memory.append(hex(i % 256))
    # print(hex(i), main_memory[i])

# Handle an R instruction
def instruction_read(c, adr):
    slot_num, tag, block_offset = bitwise_mask(adr)
    # print( hex(tag),hex(slot_num), hex(block_offset))
    cache_row = c[slot_num]
    hit_or_miss = "miss"
    if cache_row.valid == 1:  # non-blank
        if cache_row.tag == tag: # match the address
            value = cache_row.data[block_offset]
            hit_or_miss = "hit"
        elif cache_row.dirty == 0: # dismatch the address and the current data is clean: fetch required data from the main memory
            value = fetch_date_from_main_mem(cache_row, adr)
        else: #  cache_row.dirty == 1,  dismatch the address and the current data is dirty: update the main memory data and fetch required data
            # update the main_memory
            begin_addr = from_cache_to_addr(cache_row)
            for i in range(16):
                main_memory[begin_addr + i] = cache_row.data[i]
            # fetch the new block from main_memory to cache, and set the dirty to zero
            value = fetch_date_from_main_mem(cache_row, adr)
            cache_row.dirty = 0
    else: # blank: fetch the required data from main memory
        value = fetch_date_from_main_mem(cache_row, adr)
    return hit_or_miss, value

# Handle a W instruction
def instruction_write(c, adr, val):
    slot_num, tag, block_offset = bitwise_mask(adr)
    cache_row = c[slot_num]
    hit_or_miss = "miss"
    # print( hex(tag), hex(slot_num),hex(block_offset))
    if cache_row.valid == 0: # blank block: fetch the required block from main_memory, update the cache, set dirty = 1
        fetch_date_from_main_mem(cache_row, adr)
        cache_row.data[block_offset] = hex(val)
    else: # valid == 1, none-blank
        if cache_row.tag == tag:  # matched, write new data to the cache block, set dirty = 1
            cache_row.data[block_offset] = hex(val)
            hit_or_miss = "hit"
        elif cache_row.dirty == 1: # unmatched, dirty block: update the cache block to the main memory, and fetch the required block from it and then write the cache, set dirty = 1
            # update the main_memory
            begin_addr = from_cache_to_addr(cache_row)
            for i in range(16):
                main_memory[begin_addr + i] = cache_row.data[i]
            # fetch the new block from main_memory to cache
            fetch_date_from_main_mem(cache_row, adr)
            # update value
            cache_row.data[block_offset] = hex(val)
        else: # unmatched, non-dirty block: fetch the required block from main memory, write the cache, set dirty = 1
            fetch_date_from_main_mem(cache_row, adr)
            cache_row.data[block_offset] = hex(val)
    cache_row.dirty = 1
    return hit_or_miss

# Handle a D instruction
def instruction_display(c):
    # cache_table = 'Slot\tValid\tTag\tDirty\tData\n'
    # for item in c:
    #     cache_table += f"{item.slot}\t\t{item.valid}\t\t{item.tag}\t{item.dirty}\t\t{item.data}\n"
    # print(cache_table)


    # Print header
    print('Slot\tValid\tTag\tDirty\tData')

    # Format each row according to the style in the image
    for item in c:
        # Convert slot to hex if it's a numerical slot (0-15 = 0-F)
        slot_display = format(item.slot, 'X') if isinstance(item.slot, int) else item.slot

        # Print the initial columns
        print(f"{slot_display}\t{item.valid}\t{item.tag}\t{item.dirty}", end="\t ")

        # Format the data array into space-separated hex values
        data_str = ""
        for val in item.data:
            # Handle different formats of data
            if isinstance(val, str) and val.startswith('0x'):
                # Remove '0x' prefix and ensure 2 digits
                hex_val = val[2:].zfill(2).upper()
            elif val == 0:
                hex_val = "00"
            else:
                # Convert integer to 2-digit hex string
                hex_val = format(val, '02X')

            data_str += hex_val + " "

        # Print the formatted data
        print(data_str)


# Extract attributes from an address
def bitwise_mask(adr):
    block_size_mask = 0x0000000F
    slot_mask = 0x000000F0
    tag_mask = 0xFFFFFF00
    block_offset = adr & block_size_mask
    slot_num = (adr & slot_mask) >> 4
    tag = (adr & tag_mask) >> 8
    return slot_num, tag, block_offset

# Find the beginning and end address for a block
def begin_and_end_block_address(adr):
    mask = 0xFFFFFFF0
    begin_addr = mask & adr
    end_addr = (mask & adr) + 0xF
    return begin_addr, end_addr

# Find the beginning address of a given block in the cache
def from_cache_to_addr(cache_row):
    begin_addr = (cache_row.slot << 4) + (cache_row.tag << 8) + 0x0
    return begin_addr

# Fetcg the data from the main memory to the cache
def fetch_date_from_main_mem(cache_row, adr):
    slot_num, tag, block_offset = bitwise_mask(adr)
    begin_addr, end_addr = begin_and_end_block_address(adr)
    sliced_block = main_memory[begin_addr:end_addr + 1]
    cache_row.data = sliced_block
    cache_row.tag = tag
    cache_row.valid = 1
    value = cache_row.data[block_offset]
    return value

# Read input file
with open("input.txt", "r") as file:
    for line in file:
        # print(line.strip())
        instruction_set.append(line.strip())

# Read instructions one by one and implement them
for index in range(len(instruction_set)):

    # Read an R instruction
    if instruction_set[index] == "R":
        addr = int(instruction_set[index + 1], 16)
        hit_or_miss, value = instruction_read(cache, addr)
        print(f"(R)ead, (W)rite, or (D)isplay Cache?\nR"
              f"\nWhat address would you like to read?"
              f"\n{instruction_set[index+1]}\n"
              f"At that byte there is the value {value} "
              f"(Cache {hit_or_miss})"
              f"\n-----------------")

    # Read an W instruction
    if instruction_set[index] == "W":
        addr = int(instruction_set[index + 1], 16)
        value = int(instruction_set[index + 2], 16)
        hit_or_miss = instruction_write(cache, addr, value)
        print(f"(R)ead, (W)rite, or (D)isplay Cache?\nW"
              f"\nWhat address would you like to write to?"
              f"\n{instruction_set[index+1]}\n"
              f"What data would you like to write at that address?\n{instruction_set[index+2]}\n"
              f"Value {instruction_set[index+2]} has been written to address {instruction_set[index+1]} "
              f"(Cache {hit_or_miss})"
              f"\n-----------------")

    # Read a D instruction
    if instruction_set[index] == "D":
        print(f"(R)ead, (W)rite, or (D)isplay Cache?\nD")
        instruction_display(cache)
        print("-----------------")
