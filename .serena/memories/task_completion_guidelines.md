# F95Checker Task Completion Guidelines

## Pre-Development Checklist

### Environment Setup
- [ ] Python 3.11+ installed and verified
- [ ] Virtual environment created and activated
- [ ] Development dependencies installed (`pip install -r requirements-dev.txt`)
- [ ] Git configured with proper user settings
- [ ] IDE/editor configured for Python development

### Code Quality Standards
- [ ] Type hints added to all functions and methods
- [ ] Docstrings written in Google style format
- [ ] Code follows project naming conventions (snake_case, PascalCase, etc.)
- [ ] Import statements organized (standard library, third-party, local)
- [ ] No circular import issues
- [ ] Error handling implemented appropriately

### Testing Requirements
- [ ] Unit tests written for new functionality
- [ ] Integration tests created for component interactions
- [ ] Async tests use pytest-asyncio
- [ ] Mock external dependencies appropriately
- [ ] Test coverage maintained or improved

## Development Process

### Feature Development
1. **Planning Phase**
   - [ ] Understand requirements and scope
   - [ ] Identify affected modules and files
   - [ ] Design API interfaces and data structures
   - [ ] Consider cross-platform compatibility

2. **Implementation Phase**
   - [ ] Create feature branch from main
   - [ ] Implement core functionality
   - [ ] Add proper error handling
   - [ ] Implement logging where appropriate
   - [ ] Add configuration options if needed

3. **Testing Phase**
   - [ ] Run unit tests locally
   - [ ] Test on multiple platforms if possible
   - [ ] Verify debug mode functionality
   - [ ] Test error scenarios and edge cases

### Bug Fix Process
1. **Investigation**
   - [ ] Reproduce the bug consistently
   - [ ] Identify root cause
   - [ ] Check for similar issues in codebase
   - [ ] Review recent changes that might be related

2. **Fix Implementation**
   - [ ] Implement minimal fix
   - [ ] Add regression test
   - [ ] Update documentation if needed
   - [ ] Verify fix doesn't break existing functionality

## Code Review Checklist

### Functionality Review
- [ ] Code implements required functionality
- [ ] Edge cases are handled properly
- [ ] Error conditions are managed gracefully
- [ ] Performance impact is acceptable
- [ ] Security considerations addressed

### Code Quality Review
- [ ] Code is readable and well-organized
- [ ] Naming conventions followed consistently
- [ ] Type hints are accurate and complete
- [ ] Docstrings are clear and comprehensive
- [ ] No obvious code smells or anti-patterns

### Architecture Review
- [ ] Follows project architecture patterns
- [ ] Proper separation of concerns
- [ ] Dependencies are managed correctly
- [ ] Cross-platform compatibility maintained
- [ ] Integration points are well-defined

## Pre-Commit Checklist

### Code Quality
- [ ] All tests pass locally
- [ ] Code formatting is consistent
- [ ] No linting errors or warnings
- [ ] Type checking passes (if using mypy)
- [ ] Documentation is updated

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance testing (if applicable)
- [ ] Cross-platform testing (if possible)

### Documentation
- [ ] Code comments updated
- [ ] Docstrings complete and accurate
- [ ] README updated (if needed)
- [ ] CHANGELOG updated
- [ ] API documentation updated (if applicable)

## Build and Release Process

### Pre-Build Verification
- [ ] All tests pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Version number updated in `common/meta.py`
- [ ] Build dependencies available

### Build Commands
```bash
# Development build
python setup.py build

# Release build (mark as release first)
# Edit common/meta.py: release = True
python setup.py build

# Browser extension build
python setup.py browser
```

### Build Verification
- [ ] Executable runs without errors
- [ ] All features work as expected
- [ ] No missing dependencies
- [ ] Platform-specific features work
- [ ] Debug mode functions properly

### Release Process
1. **Preparation**
   - [ ] Update version in `common/meta.py`
   - [ ] Update CHANGELOG.md
   - [ ] Create release commit with tag
   - [ ] Push to GitHub

2. **CI/CD**
   - [ ] GitHub Actions build triggered
   - [ ] All platform builds complete successfully
   - [ ] Artifacts uploaded to GitHub
   - [ ] Release notes prepared

3. **Post-Release**
   - [ ] Test release builds
   - [ ] Update documentation
   - [ ] Notify users of release
   - [ ] Monitor for issues

## Testing Guidelines

### Test Categories
1. **Unit Tests**
   - Test individual functions and methods
   - Mock external dependencies
   - Cover edge cases and error conditions
   - Run quickly and independently

2. **Integration Tests**
   - Test component interactions
   - Test database operations
   - Test API integrations
   - Test GUI interactions

3. **Performance Tests**
   - Test large dataset handling
   - Test memory usage
   - Test response times
   - Test concurrent operations

### Test Execution
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=modules

# Run async tests
pytest tests/test_async.py -v
```

### Test Data Management
- [ ] Use factories for test data creation
- [ ] Clean up test data after tests
- [ ] Use temporary directories for file operations
- [ ] Mock network requests appropriately
- [ ] Use in-memory databases for testing

## Debugging Guidelines

### Debug Mode Usage
```bash
# Enable debug mode
set F95DEBUG=1
python main.py

# Or use debug script
python main-debug.py
```

### Common Debugging Techniques
1. **Logging**
   - Use appropriate log levels
   - Include context information
   - Log function entry/exit points
   - Log error details with stack traces

2. **Debugging Tools**
   - Use Python debugger (pdb/ipdb)
   - Use IDE debugging features
   - Use logging for production debugging
   - Use profiling tools for performance issues

3. **Error Analysis**
   - Check log files for errors
   - Use debug mode for detailed output
   - Monitor system resources
   - Check network traffic if applicable

### Common Issues and Solutions
1. **Import Errors**
   - Check Python path
   - Verify virtual environment
   - Check for circular imports
   - Verify package installation

2. **GUI Issues**
   - Check OpenGL drivers
   - Verify display settings
   - Check for theme conflicts
   - Test on different platforms

3. **Performance Issues**
   - Profile memory usage
   - Check async task management
   - Monitor database performance
   - Analyze network request patterns

## Documentation Standards

### Code Documentation
- [ ] All public functions have docstrings
- [ ] Complex algorithms are commented
- [ ] Workarounds are explained
- [ ] TODO and FIXME comments included
- [ ] Type hints are complete

### User Documentation
- [ ] README.md updated for new features
- [ ] Installation instructions current
- [ ] Usage examples provided
- [ ] FAQ updated if needed
- [ ] Screenshots updated if UI changed

### Developer Documentation
- [ ] API documentation updated
- [ ] Architecture decisions documented
- [ ] Migration guides provided
- [ ] Contributing guidelines current
- [ ] Development setup instructions clear

## Quality Assurance

### Code Quality Tools
- [ ] Black code formatting applied
- [ ] isort import sorting applied
- [ ] Flake8 linting passes
- [ ] MyPy type checking passes
- [ ] Bandit security scanning passes

### Security Considerations
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS prevention measures
- [ ] Secure credential handling
- [ ] Network security considerations

### Performance Monitoring
- [ ] Memory usage monitored
- [ ] CPU usage acceptable
- [ ] Network requests optimized
- [ ] Database queries efficient
- [ ] GUI rendering smooth

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Rollback plan prepared

### Deployment Process
- [ ] Build artifacts created
- [ ] Installation tested
- [ ] Configuration verified
- [ ] Monitoring enabled
- [ ] User communication prepared

### Post-Deployment
- [ ] Health checks passing
- [ ] Error monitoring active
- [ ] User feedback collected
- [ ] Performance metrics collected
- [ ] Issues tracked and resolved

## Maintenance Guidelines

### Regular Maintenance Tasks
- [ ] Dependencies updated regularly
- [ ] Security patches applied
- [ ] Performance optimizations implemented
- [ ] Documentation kept current
- [ ] Test coverage maintained

### Issue Management
- [ ] Issues categorized and prioritized
- [ ] Root cause analysis performed
- [ ] Fixes tested thoroughly
- [ ] Regression tests added
- [ ] Users informed of fixes

### Continuous Improvement
- [ ] Code quality metrics tracked
- [ ] Performance benchmarks maintained
- [ ] User feedback incorporated
- [ ] Technical debt addressed
- [ ] Best practices updated