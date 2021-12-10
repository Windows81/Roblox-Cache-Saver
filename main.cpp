#include <iostream>
#include <fstream>
#include <filesystem>
std::filesystem::path orig_path("C:\\Users\\USERNAME\\AppData\\Local\\Temp\\Roblox\\http");
std::filesystem::path save_path("C:\\Users\\USERNAME\\Documents\\Roblox");
int main() {
	char b[1024];
	for (const auto& entry : std::filesystem::directory_iterator(orig_path)) {
		std::filesystem::path rp = orig_path / entry.path().filename();
		std::filesystem::path wp = save_path / entry.path().filename();
		if (entry.file_size() <= 127)
			continue;
		std::ifstream rs(rp.c_str(), std::ios::binary);
		std::ofstream ws(wp.c_str(), std::ios::binary);
		std::streamoff off = 3000, n;
		rs.seekg(off);
		do {
			rs.seekg(off -= 4);
			rs.read(b, 2);
		} while (b[0] != 13 || b[1] != 10);
		rs.seekg(n = off - 3);
		rs.read(b, 2);
		while (b[0] != 13 || b[1] != 58) {
			rs.seekg(n -= 3);
			rs.read(b, 2);
			if (b[0] == 58)
				break;
			else if (b[0] == 13 || b[1] == 10)
				off = n;
		}
		rs.seekg(off + 2);
		ws << rs.rdbuf();
		rs.close();
		ws.close();
	}
}