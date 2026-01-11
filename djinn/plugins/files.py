"""
File Operations Plugins - File and text manipulation commands.
"""


class FindPlugin:
    """File search commands."""
    
    TEMPLATES = {
        "find_name": "find . -name '{pattern}'",
        "find_type_f": "find . -type f -name '{pattern}'",
        "find_type_d": "find . -type d -name '{pattern}'",
        "find_size_larger": "find . -size +{size}",
        "find_size_smaller": "find . -size -{size}",
        "find_modified": "find . -mtime -{days}",
        "find_empty": "find . -empty",
        "find_exec": "find . -name '{pattern}' -exec {command} {{}} \\;",
        "find_delete": "find . -name '{pattern}' -delete",
        "locate": "locate {pattern}",
        "which": "which {command}",
        "whereis": "whereis {command}",
    }


class GrepPlugin:
    """Text search commands."""
    
    TEMPLATES = {
        "grep": "grep '{pattern}' {file}",
        "grep_recursive": "grep -r '{pattern}' .",
        "grep_files": "grep -l '{pattern}' *",
        "grep_count": "grep -c '{pattern}' {file}",
        "grep_number": "grep -n '{pattern}' {file}",
        "grep_ignore_case": "grep -i '{pattern}' {file}",
        "grep_invert": "grep -v '{pattern}' {file}",
        "grep_context": "grep -C 3 '{pattern}' {file}",
        "grep_extended": "grep -E '{regex}' {file}",
        "ripgrep": "rg '{pattern}'",
        "ripgrep_type": "rg -t {type} '{pattern}'",
        "ag": "ag '{pattern}'",
    }


class SedPlugin:
    """Stream editor commands."""
    
    TEMPLATES = {
        "replace": "sed 's/{old}/{new}/' {file}",
        "replace_all": "sed 's/{old}/{new}/g' {file}",
        "replace_inplace": "sed -i 's/{old}/{new}/g' {file}",
        "delete_line": "sed '{n}d' {file}",
        "delete_pattern": "sed '/{pattern}/d' {file}",
        "print_range": "sed -n '{start},{end}p' {file}",
        "insert_before": "sed '{n}i {text}' {file}",
        "insert_after": "sed '{n}a {text}' {file}",
    }


class AwkPlugin:
    """Awk text processing commands."""
    
    TEMPLATES = {
        "print_column": "awk '{{print ${n}}}' {file}",
        "print_columns": "awk '{{print $1, $2}}' {file}",
        "sum_column": "awk '{{sum += ${n}}} END {{print sum}}' {file}",
        "count_lines": "awk 'END {{print NR}}' {file}",
        "filter": "awk '${n} == \"{value}\"' {file}",
        "delimiter": "awk -F'{delimiter}' '{{print $1}}' {file}",
    }


class TextPlugin:
    """Text manipulation commands."""
    
    TEMPLATES = {
        "cat": "cat {file}",
        "head": "head -n {n} {file}",
        "tail": "tail -n {n} {file}",
        "tail_follow": "tail -f {file}",
        "wc_lines": "wc -l {file}",
        "wc_words": "wc -w {file}",
        "wc_chars": "wc -c {file}",
        "sort": "sort {file}",
        "sort_reverse": "sort -r {file}",
        "sort_numeric": "sort -n {file}",
        "uniq": "uniq {file}",
        "uniq_count": "uniq -c {file}",
        "cut_field": "cut -d'{delimiter}' -f{n} {file}",
        "cut_chars": "cut -c{start}-{end} {file}",
        "paste": "paste {file1} {file2}",
        "join": "join {file1} {file2}",
        "tr": "tr '{old}' '{new}'",
        "tr_delete": "tr -d '{chars}'",
        "rev": "rev {file}",
        "tac": "tac {file}",
    }


class FilePlugin:
    """File operations commands."""
    
    TEMPLATES = {
        "ls": "ls -la",
        "ls_human": "ls -lah",
        "ls_time": "ls -lt",
        "ls_size": "ls -lS",
        "tree": "tree",
        "tree_depth": "tree -L {depth}",
        "cp": "cp {source} {destination}",
        "cp_recursive": "cp -r {source} {destination}",
        "mv": "mv {source} {destination}",
        "rm": "rm {file}",
        "rm_recursive": "rm -rf {directory}",
        "mkdir": "mkdir {directory}",
        "mkdir_parents": "mkdir -p {path}",
        "touch": "touch {file}",
        "ln_symbolic": "ln -s {target} {link}",
        "ln_hard": "ln {target} {link}",
        "file": "file {file}",
        "stat": "stat {file}",
        "realpath": "realpath {file}",
        "basename": "basename {path}",
        "dirname": "dirname {path}",
    }


class ArchivePlugin:
    """Archive commands."""
    
    TEMPLATES = {
        "tar_create": "tar -czvf {archive}.tar.gz {directory}",
        "tar_extract": "tar -xzvf {archive}.tar.gz",
        "tar_list": "tar -tzvf {archive}.tar.gz",
        "tar_bz2_create": "tar -cjvf {archive}.tar.bz2 {directory}",
        "tar_bz2_extract": "tar -xjvf {archive}.tar.bz2",
        "zip_create": "zip -r {archive}.zip {directory}",
        "zip_extract": "unzip {archive}.zip",
        "zip_list": "unzip -l {archive}.zip",
        "gzip": "gzip {file}",
        "gunzip": "gunzip {file}.gz",
        "7z_create": "7z a {archive}.7z {directory}",
        "7z_extract": "7z x {archive}.7z",
        "rar_extract": "unrar x {archive}.rar",
    }


class DiffPlugin:
    """File comparison commands."""
    
    TEMPLATES = {
        "diff": "diff {file1} {file2}",
        "diff_unified": "diff -u {file1} {file2}",
        "diff_side": "diff -y {file1} {file2}",
        "diff_brief": "diff -q {file1} {file2}",
        "diff_recursive": "diff -rq {dir1} {dir2}",
        "colordiff": "colordiff {file1} {file2}",
        "vimdiff": "vimdiff {file1} {file2}",
        "comm": "comm {file1} {file2}",
        "cmp": "cmp {file1} {file2}",
    }


class EncodingPlugin:
    """Encoding and decoding commands."""
    
    TEMPLATES = {
        "base64_encode": "echo -n '{text}' | base64",
        "base64_decode": "echo '{encoded}' | base64 -d",
        "base64_file": "base64 {file}",
        "url_encode": "python3 -c \"import urllib.parse; print(urllib.parse.quote('{text}'))\"",
        "url_decode": "python3 -c \"import urllib.parse; print(urllib.parse.unquote('{text}'))\"",
        "hex_encode": "xxd {file}",
        "hex_decode": "xxd -r {file}",
        "md5": "md5sum {file}",
        "sha1": "sha1sum {file}",
        "sha256": "sha256sum {file}",
        "sha512": "sha512sum {file}",
    }


class JqPlugin:
    """JSON processing commands."""
    
    TEMPLATES = {
        "pretty": "jq '.' {file}",
        "field": "jq '.{field}' {file}",
        "array": "jq '.[]' {file}",
        "filter": "jq '.[] | select(.{field} == \"{value}\")' {file}",
        "keys": "jq 'keys' {file}",
        "length": "jq 'length' {file}",
        "sort": "jq 'sort_by(.{field})' {file}",
        "compact": "jq -c '.' {file}",
        "raw": "jq -r '.{field}' {file}",
    }


class YqPlugin:
    """YAML processing commands."""
    
    TEMPLATES = {
        "read": "yq '.' {file}",
        "field": "yq '.{field}' {file}",
        "set": "yq -i '.{field} = \"{value}\"' {file}",
        "delete": "yq -i 'del(.{field})' {file}",
        "to_json": "yq -o=json '.' {file}",
        "from_json": "yq -P '.' {file}.json",
    }
