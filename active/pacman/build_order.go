package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"sort"
	"strings"

	alpm "github.com/Jguer/go-alpm/v2"
)

// DepNode represents a package and its dependencies
type DepNode struct {
	Name         string
	Dependencies map[string]bool // set of dependency names
	Visited      bool
	InStack      bool
}

// BuildOrderResolver resolves the build order of dependencies
type BuildOrderResolver struct {
	packages map[string]*DepNode
	order    []string
}

// NewBuildOrderResolver creates a new resolver
func NewBuildOrderResolver() *BuildOrderResolver {
	return &BuildOrderResolver{
		packages: make(map[string]*DepNode),
		order:    []string{},
	}
}

// AddPackage adds a package to the resolver
func (r *BuildOrderResolver) AddPackage(pkg alpm.IPackage) {
	if _, exists := r.packages[pkg.Name()]; exists {
		return
	}

	node := &DepNode{
		Name:         pkg.Name(),
		Dependencies: make(map[string]bool),
		Visited:      false,
		InStack:      false,
	}

	// Add all dependencies (both depends and makedepends)
	addDepsToNode(node, pkg.Depends().Slice())
	addDepsToNode(node, pkg.MakeDepends().Slice())

	r.packages[pkg.Name()] = node
}

// addDepsToNode extracts dependency names and adds them to the node
func addDepsToNode(node *DepNode, deps []alpm.Depend) {
	for _, dep := range deps {
		depName := dep.Name
		node.Dependencies[depName] = true
	}
}

// ResolveDependencies recursively resolves all dependencies
func (r *BuildOrderResolver) ResolveDependencies(handle *alpm.Handle, pkgName string) error {
	// Get local database
	localDB, err := handle.LocalDB()
	if err != nil {
		return fmt.Errorf("failed to get local database: %w", err)
	}

	// Try to find in local database first
	pkg := localDB.Pkg(pkgName)
	if pkg == nil {
		// If not in local, try sync databases
		syncDBs, err := handle.SyncDBs()
		if err != nil {
			return fmt.Errorf("failed to get sync databases: %w", err)
		}

		for _, db := range syncDBs.Slice() {
			pkg = db.Pkg(pkgName)
			if pkg != nil {
				break
			}
		}
	}

	if pkg == nil {
		return fmt.Errorf("package '%s' not found", pkgName)
	}

	return r.resolveDependenciesRecursive(handle, pkg)
}

// resolveDependenciesRecursive recursively resolves dependencies
func (r *BuildOrderResolver) resolveDependenciesRecursive(handle *alpm.Handle, pkg alpm.IPackage) error {
	// Add the package itself
	r.AddPackage(pkg)

	// Get databases
	localDB, _ := handle.LocalDB()
	syncDBs, err := handle.SyncDBs()
	if err != nil {
		return err
	}

	// Process both Depends and MakeDepends
	allDeps := append(pkg.Depends().Slice(), pkg.MakeDepends().Slice()...)

	for _, dep := range allDeps {
		depName := dep.Name
		if _, exists := r.packages[depName]; exists {
			// Already processed
			continue
		}

		// Find the dependency in local or sync databases
		var depPkg alpm.IPackage

		if localDB != nil {
			depPkg = localDB.Pkg(depName)
		}

		if depPkg == nil {
			for _, db := range syncDBs.Slice() {
				depPkg = db.Pkg(depName)
				if depPkg != nil {
					break
				}
			}
		}

		if depPkg != nil {
			if err := r.resolveDependenciesRecursive(handle, depPkg); err != nil {
				// Log warning but continue, as some dependencies might be provided by other packages
				log.Printf("Warning: could not resolve dependency '%s': %v\n", depName, err)
			}
		} else {
			// Dependency not found in any database - might be provided by another package
			log.Printf("Warning: dependency '%s' not found in any database\n", depName)
		}
	}

	return nil
}

// SortTopological performs topological sort to determine build order
func (r *BuildOrderResolver) SortTopological() ([]string, error) {
	// Create a copy of packages for sorting
	visited := make(map[string]bool)
	inStack := make(map[string]bool)
	var result []string
	var cycleError error

	var visit func(name string)
	visit = func(name string) {
		if visited[name] {
			return
		}

		if inStack[name] {
			cycleError = fmt.Errorf("circular dependency detected involving package '%s'", name)
			return
		}

		inStack[name] = true

		if node, exists := r.packages[name]; exists {
			// Visit all dependencies first
			for depName := range node.Dependencies {
				if depPkg, ok := r.packages[depName]; ok {
					visit(depPkg.Name)
				}
				// If dependency not in packages, it might be external or provided
			}
		}

		inStack[name] = false
		visited[name] = true
		result = append(result, name)
	}

	// Visit all packages
	for pkgName := range r.packages {
		if !visited[pkgName] {
			visit(pkgName)
			if cycleError != nil {
				return nil, cycleError
			}
		}
	}

	return result, nil
}

// PrintBuildOrder prints the build order in a readable format
func (r *BuildOrderResolver) PrintBuildOrder(buildOrder []string) {
	fmt.Println("Build Order:")
	fmt.Println(strings.Repeat("-", 50))
	for i, pkgName := range buildOrder {
		fmt.Printf("%d. %s\n", i+1, pkgName)
	}
	fmt.Println(strings.Repeat("-", 50))
	fmt.Printf("Total packages to build: %d\n", len(buildOrder))
}

// PrintDependencyTree prints the dependency tree
func (r *BuildOrderResolver) PrintDependencyTree(pkgName string, indent string, visited map[string]bool) {
	if visited[pkgName] {
		fmt.Printf("%s%s (circular)\n", indent, pkgName)
		return
	}

	fmt.Printf("%s%s\n", indent, pkgName)

	if node, exists := r.packages[pkgName]; exists {
		visited[pkgName] = true

		// Sort dependencies for consistent output
		var depNames []string
		for depName := range node.Dependencies {
			depNames = append(depNames, depName)
		}
		sort.Strings(depNames)

		for i, depName := range depNames {
			if i == len(depNames)-1 {
				fmt.Printf("%s└── ", indent)
				r.PrintDependencyTree(depName, indent+"    ", visited)
			} else {
				fmt.Printf("%s├── ", indent)
				r.PrintDependencyTree(depName, indent+"│   ", visited)
			}
		}
	}
}

func main() {
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "Usage: %s [options] <package>\n", os.Args[0])
		fmt.Fprintf(flag.CommandLine.Output(), "Outputs the build order of package dependencies\n\n")
		flag.PrintDefaults()
	}

	tree := flag.Bool("tree", false, "Print dependency tree instead of build order")
	debug := flag.Bool("debug", false, "debug")
	flag.Parse()

	args := flag.Args()
	if len(args) != 1 {
		flag.Usage()
		os.Exit(1)
	}

	pkgName := args[0]

	// Initialize pacman library
	handle, err := alpm.Initialize("/", "/var/lib/pacman")
	if err != nil {
		log.Fatalf("Failed to initialize alpm: %v", err)
	}
	defer handle.Release()

	if *debug {
		d(handle)
		return
	}

	// Create resolver and resolve dependencies
	resolver := NewBuildOrderResolver()
	if err := resolver.ResolveDependencies(handle, pkgName); err != nil {
		log.Fatalf("Error: %v", err)
	}

	if *tree {
		fmt.Printf("Dependency Tree for %s:\n", pkgName)
		fmt.Println(strings.Repeat("-", 50))
		resolver.PrintDependencyTree(pkgName, "", make(map[string]bool))
	} else {
		// Perform topological sort
		buildOrder, err := resolver.SortTopological()
		if err != nil {
			log.Fatalf("Error determining build order: %v", err)
		}

		resolver.PrintBuildOrder(buildOrder)
	}
}

func d(handle *alpm.Handle) {
	handle.RegisterSyncDB("core", 0)
	handle.RegisterSyncDB("community", 0)
	handle.RegisterSyncDB("extra", 0)

	db, err := handle.SyncDBByName("core")
	if err != nil {
		panic(err)
	}
	pkg := db.Pkg("pacman")
	for _, dep := range pkg.MakeDepends().Slice() {
		fmt.Println(dep)
	}
	for _, prov := range pkg.Provides().Slice() {
		fmt.Println(prov)
	}
}
