local M = {}

function M:peek(job)
	local child, err = Command("glow")
		:args({ "--style", "dark", "--width", tostring(job.area.w), job.file.url:to_string() })
		:stdout(Command.PIPED)
		:stderr(Command.NULL)
		:spawn()

	if not child then
		ya.err("glow preview failed: " .. tostring(err))
		return
	end

	local limit = job.area.h
	local i, lines = 0, ""
	repeat
		local line, event = child:read_line()
		if event ~= 0 then break end
		i = i + 1
		if i > job.skip then
			lines = lines .. line
		end
	until i >= job.skip + limit

	child:start_kill()

	if job.skip > 0 and i < job.skip + limit then
		ya.manager_emit("peek", { math.max(0, i - limit), only_if = job.file.url })
		return
	end

	local output = ui.Text.parse(lines):area(job.area)
	ya.preview_widgets(job, { output })
end

function M:seek(job)
	local h = cx.active.current.hovered
	if h and h.url == job.file.url then
		local step = math.floor(job.units * job.area.h / 10)
		ya.manager_emit("peek", {
			math.max(0, cx.active.preview.skip + step),
			only_if = job.file.url,
		})
	end
end

return M
